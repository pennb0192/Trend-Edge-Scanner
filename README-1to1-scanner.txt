# 1:1 Rule — Trend Edge Scanner (Windows Quick Guide)

## Step 1. Open Command Prompt
- Press Windows key, type "cmd", hit Enter.

## Step 2. Navigate to your folder
Type:
cd Desktop\1to1_scanner
and press Enter.

## Step 3. Create a virtual environment (optional but recommended)
py -m venv venv
venv\Scripts\activate

## Step 4. Install packages
pip install -r requirements.txt

## Step 5. Run the command-line scanner
python scanner.py -s "SPY,AAPL,MSFT" --period 6mo --interval 1d --tolerance 0.00 --csv results.csv

## Step 6. Run the app (point-and-click)
streamlit run app.py
- Browser will open, paste tickers, click "Run Scan".

## Step 7. Exit the environment when done
deactivate

---

NOTES:
- scanner.py = runs in Command Prompt
- app.py = runs a Streamlit app in your browser
- requirements.txt = list of needed Python packages
- tickers_example.txt = sample list of stocks
- README-1to1-scanner.txt = this guide :)
