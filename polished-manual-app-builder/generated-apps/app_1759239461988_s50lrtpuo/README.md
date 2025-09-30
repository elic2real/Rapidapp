# ADemoCrmApp

A demo CRM app with authentication, dashboard, and notifications. Stack: nextjs-postgres

## ✨ Features

- User Authentication
- Real-time Updates
- Admin Dashboard
- Email Notifications

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- PostgreSQL database

### Installation

1. Clone this repository
```bash
git clone <repository-url>
cd ademocrmapp
```

2. Install dependencies
```bash
npm install
```

3. Set up environment variables
```bash
cp .env.example .env.local
```

4. Set up the database
```bash
npx prisma generate
npx prisma db push
```

5. Start the development server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## 📁 Project Structure

```
src/
├── app/                 # Next.js 13+ app directory
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home page
│   └── api/            # API routes
├── components/         # Reusable components
├── lib/               # Utility functions
└── types/             # TypeScript types
```

## 🛠️ Built With

- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **Database**: PostgreSQL with Prisma
- **Language**: TypeScript
- **Authentication**: NextAuth.js

## 📦 Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## 🚀 Deployment

This app can be deployed on platforms like:

- [Vercel](https://vercel.com)
- [Netlify](https://netlify.com)
- [Railway](https://railway.app)
- [Render](https://render.com)

## 📝 License

This project is licensed under the MIT License.

---

**Generated with ❤️ by Rapidapp AI Generator**
