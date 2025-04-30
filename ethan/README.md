# Etflix

A Netflix-inspired streaming platform for Ethans.

## 🚀 Features

- Browse and search for movies and TV shows
- Stream content with an intuitive player interface
- Continue watching functionality
- Personalized recommendations
- User profiles and preferences
- Critics & Audience Ratings integration
- Social media trending integration

## 📋 Prerequisites

- PHP 7.4 or higher
- MySQL/MariaDB
- Python 3.8+ (for scraping scripts)
- Web server (Apache/Nginx)

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/etbars/etflix.git
   cd etflix
   ```

2. Set up the database:
   ```bash
   mysql -u username -p database_name < categories.sql
   mysql -u username -p database_name < entities.sql
   mysql -u username -p database_name < videos.sql
   ```

3. Configure database connection:
   ```bash
   cp includes/config.sample.php includes/config.php
   # Edit config.php with your database credentials
   ```

4. Set up environment variables:
   ```bash
   cp .env.sample .env
   # Edit .env with your API keys and configuration
   ```

5. Install Python dependencies for scraping scripts:
   ```bash
   pip install -r requirements.txt
   ```

6. Start the server:
   ```bash
   php -S localhost:8000
   ```

## 🏗️ Project Structure

```
etflix/
├── ajax/                  # AJAX request handlers
├── api/                   # API endpoints
├── assets/                # Static assets (CSS, JS, images)
├── entities/              # Media files and thumbnails
├── includes/              # PHP includes and classes
│   ├── classes/           # PHP classes
│   └── config.php         # Database configuration
├── scripts/               # Python scripts for data fetching
├── .env                   # Environment variables
├── categories.sql         # Category data
├── entities.sql           # Movies and TV shows data
├── videos.sql             # Video metadata
└── index.php              # Main entry point
```

## 📱 Key Components

### Frontend

- **Homepage**: Displays featured content, categories, and recommendations
- **Entity Page**: Shows details for a specific movie or TV show
- **Watch Page**: Video player with controls and continue watching functionality
- **Search Page**: Search results with filtering options
- **Explore Page**: Interactive content discovery with ratings and social trends

### Backend

- **Entity System**: Manages movies, TV shows, and their metadata
- **User Management**: Handles user accounts, profiles, and viewing history
- **Recommendation Engine**: Generates personalized content suggestions
- **External APIs**: Integrates with TMDB and social media platforms
- **Caching System**: Optimizes performance for frequently accessed data

## 🧪 Testing

Run the test suite:
```bash
php vendor/bin/phpunit
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [TMDB](https://www.themoviedb.org/) for movie and TV show metadata
- [Font Awesome](https://fontawesome.com/) for icons
- [Bootstrap](https://getbootstrap.com/) for UI components
- [Chart.js](https://www.chartjs.org/) for data visualization