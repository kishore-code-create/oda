# Run Oil Spill Detection App (app1.py) in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Veeramalla Akshay\OneDrive\Desktop\phase 2\ODA(OIL)\oil_spill_detection\oil_spill_detection'; python app1.py" -WindowStyle Normal

# Run Oil Spill Portal App (portal_app.py) in a new window (Port 5001)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Veeramalla Akshay\OneDrive\Desktop\phase 2\OilSpillPortal'; python portal_app.py" -WindowStyle Normal
