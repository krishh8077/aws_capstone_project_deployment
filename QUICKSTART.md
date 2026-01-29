# Stock Trading Platform - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Python Requirements
```bash
pip install -r requirements.txt
```

**What this does:** Installs Flask and other necessary libraries

### Step 2: Run the Application
```bash
python app.py
```

**What this does:** Starts the Flask server on port 5000

### Step 3: Open Your Browser
Navigate to: `http://localhost:5000`

You should see the welcome landing page! 🎉

---

## 👤 First Trade Walkthrough

### 1. Create Your Account
1. Click "Get Started - Free" or go to signup page
2. Enter a username (e.g., `trader_john`)
3. Enter a password (at least 6 characters)
4. Confirm your password
5. Click "Sign Up"

✅ You now have $10,000 virtual currency!

### 2. View Your Dashboard
After login, you'll see:
- **Available Balance**: $10,000.00
- **Portfolio Value**: $0.00 (empty)
- **Total Account Value**: $10,000.00
- Quick action buttons and recent transactions

### 3. Make Your First Trade
1. Click "Buy/Sell Stocks" button or navigate to Trade page
2. In the search box, type "AAPL" (Apple Inc.)
3. Click on the Apple stock from the list
4. You'll see the stock details appear
5. Adjust quantity to 10 shares using +/- buttons
6. Click the green "Buy" button
7. See the confirmation message: ✓ Successfully bought 10 shares of AAPL

### 4. Check Your Portfolio
1. Click "Portfolio" in the navigation
2. You'll see your new position:
   - **Symbol**: AAPL
   - **Shares**: 10
   - **Avg Price**: $182.45
   - **Current Price**: $182.45
   - **Total Value**: $1,824.50

### 5. Sell Some Shares
1. Go back to Trade page
2. Search for "AAPL"
3. Click on it
4. Change quantity to 5
5. Click red "Sell" button
6. Confirmation: ✓ Successfully sold 5 shares of AAPL

### 6. View Transaction History
1. Click "History" in navigation
2. See all your trades with:
   - Buy/Sell type
   - Quantity and price
   - Total amount
   - Timestamp

---

## 🎯 Key Pages & Features

### Dashboard (`/dashboard`)
Your home page showing:
- Account balance and total value
- Current portfolio holdings
- Recent transactions
- Quick action buttons

### Trade Page (`/trade`)
Where you execute trades:
- Stock search/filter
- Stock list with prices and changes
- Stock selection panel
- Buy/sell form with quantity controls
- Trade preview showing total cost/proceeds

### Portfolio Page (`/portfolio`)
View all your holdings:
- Statistics (total holdings, value, gain/loss)
- Detailed table with:
  - Symbol and company name
  - Number of shares
  - Average purchase price
  - Current price
  - Total position value
  - Gain/loss amount and percentage

### Transactions Page (`/transactions`)
Complete trade history:
- All buy/sell orders
- Order details (quantity, price, total)
- Transaction ID and timestamp
- Status indicator

---

## 💡 Tips & Tricks

### Smart Trading Tips
1. **Start small**: Buy 1-5 shares first to understand the platform
2. **Diversify**: Try trading different stocks
3. **Monitor gains/losses**: Check portfolio regularly
4. **Track history**: Review past trades to learn

### Search Shortcut
- Press `Ctrl+K` (or `Cmd+K` on Mac) to quickly focus the search box

### Quick Access
- Use the navigation menu to jump between pages
- Use breadcrumbs or back buttons to navigate

### Mobile Friendly
- The platform works great on phones and tablets
- Try rotating your device to see responsive design

---

## 📊 Available Stocks

Start trading with these popular stocks:

| Symbol | Company | Price (Example) |
|--------|---------|-----------------|
| AAPL   | Apple Inc. | $182.45 |
| GOOGL  | Alphabet Inc. | $140.82 |
| MSFT   | Microsoft Corp. | $380.61 |
| AMZN   | Amazon.com Inc. | $181.92 |
| TSLA   | Tesla Inc. | $238.45 |
| META   | Meta Platforms | $485.72 |
| NFLX   | Netflix Inc. | $247.18 |
| NVIDIA | NVIDIA Corp. | $875.29 |

---

## ❓ FAQ

### Q: Can I lose real money?
**A:** No! This is completely simulated. No real money is involved.

### Q: What happens to my account if I close the browser?
**A:** Your account data is saved. Just log back in and your portfolio will be there!

### Q: Can I reset my balance?
**A:** Delete the `trading_data.json` file and recreate your account to start fresh.

### Q: How are stock prices updated?
**A:** Currently, prices are static for simulation purposes. For real-time prices, integrate a stock API.

### Q: Can I have multiple accounts?
**A:** Yes! Each username gets its own separate account and portfolio.

### Q: What's the maximum I can buy?
**A:** You can buy as many shares as your balance allows.

### Q: Can I short sell (sell stocks I don't own)?
**A:** No, this platform only allows you to sell stocks you currently own.

---

## 🔧 Customization Guide

### Change Starting Balance
In `app.py`, find:
```python
'balance': 10000.00,
```
Change to desired amount.

### Add More Stocks
In `app.py`, add to `STOCK_DATABASE`:
```python
'TSLA': {'name': 'Tesla Inc.', 'price': 238.45, 'change': 5.67},
```

### Change App Name
In `base.html`, find:
```html
<span>StockTrade</span>
```
Change to your preferred name.

### Modify Color Scheme
In `static/style.css`, update CSS variables:
```css
:root {
    --primary-color: #2563eb;  /* Change this */
    --success-color: #10b981;  /* And this */
    /* ... etc */
}
```

---

## 🐛 Troubleshooting

### "Address already in use" Error
**Problem:** Port 5000 is already in use
**Solution:** 
```bash
python app.py  # Will automatically try port 5001, 5002, etc.
# Or manually change port in app.py
```

### Stocks Not Showing Up
**Problem:** Stock list is empty
**Solution:** Refresh page or check browser console for errors

### Can't Login After Signup
**Problem:** Login fails after creating account
**Solution:** 
- Make sure you're using correct username/password
- Check that `trading_data.json` exists
- Try clearing browser cookies

### CSS Not Applied / Page Looks Wrong
**Problem:** Styling looks broken
**Solution:**
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh page (Ctrl+Shift+R)
- Check that `static/style.css` exists

### JavaScript Errors in Console
**Problem:** Seeing errors in browser developer tools
**Solution:**
- Refresh page
- Check browser console (F12)
- Ensure JavaScript is enabled

---

## 📈 Next Steps

1. **Explore the interface** - Get familiar with all pages
2. **Make several trades** - Buy and sell different stocks
3. **Monitor your portfolio** - Watch your gains/losses
4. **Analyze transactions** - Review your trading history
5. **Learn and improve** - Use it as a learning tool

---

## 🎓 Learning Outcomes

By using this platform, you'll learn:
- ✅ How to buy and sell stocks
- ✅ Understanding gain/loss calculations
- ✅ Portfolio diversification
- ✅ Risk management (with virtual money!)
- ✅ Market terminology and concepts

---

## 📞 Support

If you encounter issues:
1. Check this guide's Troubleshooting section
2. Review the main README.md
3. Check browser console (F12) for errors
4. Ensure Python and Flask are properly installed

---

## 🎉 You're Ready!

You now have a fully functional stock trading platform. Start exploring, making trades, and learning about the stock market!

**Happy Trading! 📊💰**

---

*For more detailed information, see README.md in the project root.*
