def categorize(description):
    desc = str(description).lower()
    if any(x in desc for x in ['pharmacy', 'medical', 'doctor', 'hospital', 'medicine']):
        return 'Medical'
    elif any(x in desc for x in ['fruit', 'vegetables', 'big bazaar', 'grocery']):
        return 'Groceries'
    elif any(x in desc for x in ['netflix', 'youtube', 'book', 'headphones', 'udemy']):
        return 'Subscriptions & Books'
    elif any(x in desc for x in ['train', 'taxi', 'ola', 'uber', 'auto', 'bus', 'rapido', 'rickshaw']):
        return 'Transportation'
    elif any(x in desc for x in ['lunch', 'dinner', 'snack', 'zomato', 'starbucks', 'ice cream', 'mcdonald', 'pizza']):
        return 'Food & Dining'
    elif any(x in desc for x in ['petrol', 'diesel', 'cng']):
        return 'Fuel'
    elif 'rent' in desc:
        return 'Rent'
    elif 'recharge' in desc:
        return 'Mobile Recharge'
    elif any(x in desc for x in ['myntra', 'jeans', 't-shirt', 'h&m', 'shirt', 'clothing']):
        return 'Clothing'
    else:
        return 'Others'
