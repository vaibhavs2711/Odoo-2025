# ReWear – Community Clothing Exchange

ReWear is a web application that promotes sustainable fashion by enabling users to exchange unused clothing with the community. The platform provides a modern, user-friendly interface for browsing, listing, and swapping clothing items.

## Features

- User registration and login
- Browse and search for clothing items
- List your own items for exchange
- Admin panel for managing users and items
- Modern, responsive UI with Bootstrap 5
- Profile picture and featured items carousel
- Category-based browsing

## Project Structure

```
Odoo-2025/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── instance/
│   └── rewear.db           # SQLite database
├── static/
│   ├── *.css               # Stylesheets
│   └── profile_picture.jpg # Profile picture (replace as needed)
├── templates/
│   ├── landing.html        # Landing page
│   ├── dashboard.html      # User dashboard
│   ├── add_item.html       # Add item form
│   ├── item_detail.html    # Item details
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   └── admin_panel.html    # Admin panel
└── WhatsApp Image ...jpeg  # Sample images
```

## Getting Started

1. **Clone the repository**
2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```
3. **Run the application**
   ```
   python app.py
   ```
4. **Open your browser** and go to `http://localhost:5000`

## Customization
- To change the profile picture on the landing page, replace the image at `static/profile_picture.jpg` with your desired image (e.g., one of the WhatsApp images).
- Add or update styles in the `static/` CSS files.

## License
This project is for educational and demonstration purposes.
