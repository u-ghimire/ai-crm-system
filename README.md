# AI-Powered CRM System

A comprehensive Customer Relationship Management system powered by artificial intelligence, built with React and Flask.

## Features

- **AI-Powered Chatbot**: Intelligent assistant for CRM operations with multi-step conversation flows
- **Customer Management**: Complete customer lifecycle tracking and relationship management
- **Contact Management**: Organized contact database with company associations
- **Deal Pipeline**: Visual pipeline management with drag-and-drop functionality
- **Task Management**: Priority-based task tracking with automated reminders
- **Sales Analytics**: Real-time dashboards and comprehensive reporting
- **Email Integration**: SendGrid integration for automated email communications
- **AI Insights**: Predictive analytics for deal success, churn risk, and smart reminders
- **Dark Mode**: Theme support for better user experience
- **Responsive Design**: Modern UI built with TailwindCSS and Framer Motion

## Tech Stack

### Frontend
- React 18
- Vite
- TailwindCSS
- Framer Motion
- Recharts
- React Hot Toast
- Axios

### Backend
- Python 3.8+
- Flask
- SQLite
- Groq AI API
- SendGrid API

## Prerequisites

Before running the application, ensure you have the following installed:

- Node.js (v16 or higher)
- Python 3.8 or higher
- pip (Python package manager)
- npm or yarn

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/u-ghimire/ai-crm-system.git
cd ai-crm-system
```

### 2. Backend Setup

Navigate to the backend directory and install dependencies:

```bash
cd ai-crm-system/backend
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the backend directory with the following variables:

```env
# Groq AI Configuration
GROQ_API_KEY=your_groq_api_key_here

# SendGrid Configuration (for email features)
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDGRID_FROM_EMAIL=your_verified_sender_email@example.com

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

**Note**: You can obtain API keys from:
- Groq AI: https://console.groq.com/
- SendGrid: https://sendgrid.com/

### 4. Initialize the Database

The database will be automatically created when you first run the backend. Optionally, you can run migrations:

```bash
python migrations/migrate_simple.py
```

### 5. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd ../frontend
npm install
```

## Running the Application

### Start the Backend Server

From the `backend` directory:

```bash
python app.py
```

The backend server will start on `http://localhost:5000`

### Start the Frontend Development Server

From the `frontend` directory (in a new terminal):

```bash
npm run dev
```

The frontend will start on `http://localhost:3001`

### Access the Application

Open your browser and navigate to:
```
http://localhost:3001
```

## Default Credentials

For testing purposes, you can use these default credentials:

- **Username**: admin
- **Password**: admin123

## Project Structure

```
ai-crm-system/
├── ai-crm-system/
│   ├── backend/
│   │   ├── app.py                 # Main Flask application
│   │   ├── requirements.txt       # Python dependencies
│   │   ├── modules/               # Backend modules
│   │   │   ├── ai_chatbot_enhanced.py
│   │   │   ├── ai_services.py
│   │   │   ├── companies.py
│   │   │   ├── contacts.py
│   │   │   ├── deals.py
│   │   │   ├── tasks_enhanced.py
│   │   │   └── ...
│   │   └── migrations/            # Database migrations
│   └── frontend/
│       ├── src/
│       │   ├── components/        # React components
│       │   │   ├── Auth/
│       │   │   ├── Chatbot/
│       │   │   ├── Companies/
│       │   │   ├── Contacts/
│       │   │   ├── Dashboard/
│       │   │   ├── Pipeline/
│       │   │   └── ...
│       │   ├── pages/             # Page components
│       │   ├── contexts/          # React contexts
│       │   └── utils/             # Utility functions
│       ├── package.json           # Node dependencies
│       └── vite.config.js         # Vite configuration
└── README.md
```

## Key Features Guide

### Chatbot Commands

The AI chatbot understands natural language commands:

- "Create a company" - Start multi-step company creation
- "Add contact John Smith" - Create a new contact
- "Create deal Enterprise License" - Create a new deal
- "Show all customers" - List customers
- "Send email to customer@example.com" - Send email
- "Create task Follow up with client" - Create a task

### Navigation

- **Dashboard**: Overview with stats, charts, and AI insights
- **Customers**: Manage customer database
- **Companies**: Company management and tracking
- **Contacts**: Contact database with company associations
- **Pipeline**: Visual deal pipeline with stage management
- **Tasks**: Task management with priority levels
- **Reports**: Comprehensive analytics and reporting
- **Settings**: User preferences and system configuration

## API Endpoints

### Authentication
- POST `/api/login` - User authentication
- POST `/api/register` - User registration

### Customers
- GET `/api/customers` - List all customers
- POST `/api/customers` - Create new customer
- PUT `/api/customers/:id` - Update customer
- DELETE `/api/customers/:id` - Delete customer

### Companies
- GET `/api/companies` - List all companies
- POST `/api/companies` - Create new company
- PUT `/api/companies/:id` - Update company
- DELETE `/api/companies/:id` - Delete company

### Contacts
- GET `/api/contacts` - List all contacts
- POST `/api/contacts` - Create new contact
- PUT `/api/contacts/:id` - Update contact
- DELETE `/api/contacts/:id` - Delete contact

### Deals/Opportunities
- GET `/api/deals` - List all deals
- POST `/api/deals` - Create new deal
- PUT `/api/deals/:id` - Update deal
- PUT `/api/deals/:id/stage` - Change deal stage
- DELETE `/api/deals/:id` - Delete deal

### Tasks
- GET `/api/tasks` - List all tasks
- POST `/api/tasks` - Create new task
- PUT `/api/tasks/:id` - Update task
- PUT `/api/tasks/:id/status` - Update task status

### AI Services
- POST `/api/chatbot/message` - Send message to AI chatbot
- GET `/api/ai/smart-reminders` - Get AI-generated reminders
- POST `/api/ai/predict-deal-success` - Predict deal win probability
- POST `/api/ai/predict-churn` - Predict customer churn risk

## Development

### Running Tests

Backend tests:
```bash
cd backend
python -m pytest
```

### Building for Production

Frontend production build:
```bash
cd frontend
npm run build
```

The built files will be in the `frontend/dist` directory.

## Troubleshooting

### Backend Issues

**Database Connection Error**
- Ensure SQLite is properly installed
- Check write permissions in the backend directory

**AI API Errors**
- Verify your Groq API key is correct in `.env`
- Check your API rate limits

**Email Sending Failures**
- Verify SendGrid API key is valid
- Ensure sender email is verified in SendGrid

### Frontend Issues

**Module Not Found**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

**API Connection Error**
- Ensure backend is running on port 5000
- Check CORS settings in backend

**Build Errors**
- Clear Vite cache: `rm -rf node_modules/.vite`
- Rebuild: `npm run dev`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License.
