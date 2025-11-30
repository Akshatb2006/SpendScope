from typing import List, Dict
import random

class AnomalyGenerator:
    
    @staticmethod
    def inject_anomalies(transactions: List[Dict], anomaly_rate: float = 0.05) -> List[Dict]:
        anomaly_count = int(len(transactions) * anomaly_rate)
        anomaly_indices = random.sample(range(len(transactions)), anomaly_count)
        
        for idx in anomaly_indices:
            txn = transactions[idx]
            anomaly_type = random.choice(["high_amount", "new_merchant", "duplicate"])
            
            if anomaly_type == "high_amount":
                txn["amount"] *= 5
                txn["description"] += " [ANOMALY]"
            
            elif anomaly_type == "new_merchant":
                txn["merchant"] = "UNKNOWN_MERCHANT_" + str(random.randint(1000, 9999))
                txn["description"] = f"{txn['merchant']} - Suspicious"
            
            elif anomaly_type == "duplicate":
                duplicate = txn.copy()
                duplicate["id"] = f"TXN_DUP_{random.randint(1000, 9999)}"
                transactions.append(duplicate)
        
        return transactions