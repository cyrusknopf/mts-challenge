# PRISM Trading Competition Leaderboard

A sleek, modern leaderboard for displaying trading competition results.

## Features

- **Modern UI**: Clean, dark-themed design with improved visibility
- **Real-time Updates**: Auto-refreshes every 30 seconds
- **Frontend Position Calculation**: Positions are calculated on the frontend based on points and profit
- **Docker Support**: Simple deployment with Docker and Docker Compose

## Getting Started

### Docker Deployment (Recommended)

The easiest way to deploy the leaderboard is with Docker:

```bash
# Clone the repository
git clone <repository-url>
cd nova-prospect-clone

# Start with Docker Compose
docker-compose up -d
```

This will build and start the application, which will be available at http://localhost:80

### Manual Installation

1. Clone the repository
```bash
git clone <repository-url>
cd nova-prospect-clone
```

2. Install dependencies
```bash
bun install
```

3. Start the development server
```bash
bun run dev
```

4. Open your browser and navigate to http://localhost:3000

## Building for Production

```bash
# Build the static site
bun run build

# The output will be in the 'out' directory
```

## Database Integration

The application is designed to be used without database connectivity, but the SQL schema is included in `setup_database.sql` for reference.

### Database Schema

The leaderboard expects a table named `leaderboard_entries` with the following structure:

```sql
CREATE TABLE leaderboard_entries (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL UNIQUE,
    points INTEGER NOT NULL DEFAULT 0,
    profit DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    last_submission_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Customization

- **Appearance**: Modify the UI components in the `src/components/ui` directory
- **Mock Data**: Adjust the sample data generation in `src/lib/mockData.ts`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
