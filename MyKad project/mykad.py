from smartcard.System import readers
from smartcard.util import toBytes
import json
from datetime import date

class MyKadReader:
    
    JPN_AID = "00 A4 04 00 0A A0 00 00 00 74 4A 50 4E 00 10"
    GET_RESPONSE = "00 C0 00 00 05"
    
    def __init__(self):
        r = readers()
        if not r:
            raise Exception("No smart card reader found in the system.")
        
        print("Connected readers detected:")
        for reader in r:
            print(f"  - {reader}")
            
        self.conn = None
        
        # Loop through all readers (built-in and USB) to find the one with the card
        for reader in r:
            try:
                conn = reader.createConnection()
                conn.connect()
                print(f"\n[SUCCESS] MyKad detected and connected in: {reader}")
                self.conn = conn
                break
            except Exception:
                # If connect() fails, this reader is empty. Move to the next one.
                continue
                
        if not self.conn:
            raise Exception("\n[ERROR] Readers found, but no MyKad detected in any of them.")
    
    def send(self, apdu_str):
        apdu = toBytes(apdu_str)
        data, sw1, sw2 = self.conn.transmit(apdu)
        return data, sw1, sw2
    
    def select_jpn(self):
        data, sw1, sw2 = self.send(self.JPN_AID)
        if sw1 == 0x61:  # more data available
            self.send(self.GET_RESPONSE)
        elif sw1 != 0x90:
            raise Exception(f"Failed to select JPN app: SW1={sw1:02X} SW2={sw2:02X}")
        return True
    
    def read_file(self, file_no, offset, length):
        """Read any section from any JPN file safely using strict Node.js chunking"""
        result = []
        remaining = length
        current_offset = offset
        
        while remaining > 0:
            # 240 bytes (0xF0) is the exact maximum safe buffer proven by the Node.js implementation
            chunk = min(remaining, 0xF0)
            
            len_lo  = chunk & 0xFF
            len_hi  = (chunk >> 8) & 0xFF
            off_lo  = current_offset & 0xFF
            off_hi  = (current_offset >> 8) & 0xFF
            
            # 1. Set Length
            set_len = f"C8 32 00 00 05 08 00 00 {len_lo:02X} {len_hi:02X}"
            self.send(set_len)
            
            # 2. Select Info
            sel_inf = f"CC 00 00 00 08 {file_no:02X} 00 01 00 {off_lo:02X} {off_hi:02X} {len_lo:02X} {len_hi:02X}"
            self.send(sel_inf)
            
            # 3. Read Info
            data, sw1, sw2 = self.send(f"CC 06 00 00 {chunk:02X}")
            
            if len(data) == 0:
                raise Exception(f"Card rejected read at offset {current_offset}. Error Code: SW1={sw1:02X} SW2={sw2:02X}")
            
            result.extend(data)
            remaining -= len(data)       
            current_offset += len(data)  
        
        return bytes(result)
    
    def decode_bcd_date(self, raw):
        """Packed BCD date: yy yy mm dd → YYYY-MM-DD"""
        hex_str = raw.hex()
        # MyKad stores full 4-digit year as the first two bytes
        year  = hex_str[0:4]  
        month = hex_str[4:6]  
        day   = hex_str[6:8]  
        return f"{year}-{month}-{day}"
    
    def decode_bcd_postcode(self, raw):
        """3 byte packed BCD: 12 34 50 → 12345"""
        return raw.hex()[0:5]
    
    def read_all(self):
        self.select_jpn()
        data = {}
        
        # === JPN FILE 1 — Personal ===
        f1 = self.read_file(0x01, 0x0003, 0x01A5) 
        
        data["name"]        = f1[0x00:0x96].decode('ascii','ignore').strip()
        data["gmpc_name"]   = f1[0x96:0xE6].decode('ascii','ignore').strip()
        data["kpt_name"]    = f1[0xE6:0x10E].decode('ascii','ignore').strip()
        data["ic"]          = f1[0x10E:0x11B].decode('ascii','ignore').strip()
        data["gender"]      = "Male" if f1[0x11B:0x11C] == b'L' else "Female"
        data["old_ic"]      = f1[0x11C:0x124].decode('ascii','ignore').strip()
        data["dob"]         = self.decode_bcd_date(f1[0x124:0x128])
        
        # --- AGE CALCULATION ---
        try:
            dob_obj = date.fromisoformat(data["dob"])
            today = date.today()
            # Calculate years difference, and subtract 1 if today's date is before their birthday this year
            age = today.year - dob_obj.year - ((today.month, today.day) < (dob_obj.month, dob_obj.day))
            data["age"] = age
        except ValueError:
            data["age"] = "Unknown"
        # -----------------------

        data["birth_place"] = f1[0x128:0x141].decode('ascii','ignore').strip()
        data["date_issued"] = self.decode_bcd_date(f1[0x141:0x145])
        data["nationality"] = f1[0x145:0x157].decode('ascii','ignore').strip()
        data["race"]        = f1[0x157:0x170].decode('ascii','ignore').strip()
        data["religion"]    = f1[0x170:0x17B].decode('ascii','ignore').strip()
        
        # === JPN FILE 2 — Photo ===
        photo_raw = self.read_file(0x02, 0x0003, 0x0FA0)
        jpeg_end = photo_raw.rfind(b'\xFF\xD9') + 2
        data["photo_bytes"] = photo_raw[:jpeg_end]
        
        # === JPN FILE 4 — Address ===
        f4 = self.read_file(0x04, 0x0003, 0x0094)
        
        data["address1"] = f4[0x00:0x1E].decode('ascii','ignore').strip()
        data["address2"] = f4[0x1E:0x3C].decode('ascii','ignore').strip()
        data["address3"] = f4[0x3C:0x5A].decode('ascii','ignore').strip()
        data["postcode"] = self.decode_bcd_postcode(f4[0x5A:0x5D])
        data["city"]     = f4[0x5D:0x76].decode('ascii','ignore').strip()
        data["state"]    = f4[0x76:0x94].decode('ascii','ignore').strip()
        
        # === JPN FILE 5 — SOCSO ===
        f5 = self.read_file(0x05, 0x0003, 0x09)
        data["socso"] = f5.decode('ascii','ignore').strip()
        
        # === JPN FILE 6 — Locality ===
        f6 = self.read_file(0x06, 0x0003, 0x0A)
        data["locality"] = f6.decode('ascii','ignore').strip()
        
        return data
    
    def save_photo(self, photo_bytes, path="photo.jpg"):
        if photo_bytes:
            with open(path, 'wb') as f:
                f.write(photo_bytes)

if __name__ == "__main__":
    try:
        reader = MyKadReader()
        result = reader.read_all()
        
        # Extract and save photo
        photo_bytes = result.pop("photo_bytes", None)
        reader.save_photo(photo_bytes, "photo.jpg")
        
        # Print JSON output
        print("\n=== MyKad Data ===")
        print(json.dumps(result, indent=2))
        print("\nPhoto saved successfully as photo.jpg")
        
    except Exception as e:
        print(f"\nExecution Failed: {str(e)}")