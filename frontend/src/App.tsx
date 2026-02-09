import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/features/auth/AuthContext'
import { LoginPage } from '@/features/auth/LoginPage'
import { HomePage } from '@/features/public/HomePage'
import { Layout } from '@/components/Layout'
import { SupplyList } from '@/features/supplies/SupplyList'
import { SupplyItemDetail } from '@/features/supplies/SupplyItemDetail'
import { AnimalList } from '@/features/animals/AnimalList'
import { AnimalMedicalRecord } from '@/features/animals/AnimalMedicalRecord'
import { AnimalDetailList } from './features/animals/AnimalDataList'
import { AnimalDataDetail } from './features/animals/AnimalDataDetail'
import { AnimalIntakesPage } from './features/animals/AnimalIntakesDetail'
import { AnimalDataEdit } from './features/animals/AnimalDataEdit'

function StaffRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Only employees can access staff panel
  const hasAccess = user?.role === 'employee'

  if (!hasAccess) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />

      {/* Staff panel routes - requires employee role */}
      <Route
        path="/panel"
        element={
          <StaffRoute>
            <Layout />
          </StaffRoute>
        }
      >
        <Route index element={<Navigate to="/panel/supplies" replace />} />
        <Route path="supplies" element={<SupplyList />} />
        <Route path="supplies/:id" element={<SupplyItemDetail />} />
        <Route path="animals-medical" element={<AnimalList />} />
        <Route path="animals-medical/:id" element={<AnimalMedicalRecord />} />
        <Route path="animals-data" element={<AnimalDetailList />} />
        <Route path="animals-data/:id" element={<AnimalDataDetail />} />
        <Route path="animals-data/:id/intakes" element={<AnimalIntakesPage />} />
        <Route path="animals-data/:id/edit" element={<AnimalDataEdit />} />
      </Route>

      {/* Redirect old routes to new panel routes */}
      <Route path="/supplies" element={<Navigate to="/panel/supplies" replace />} />
      <Route path="/supplies/:id" element={<Navigate to="/panel/supplies" replace />} />
      <Route path="/animals" element={<Navigate to="/panel/animals" replace />} />
      <Route path="/animals/:id" element={<Navigate to="/panel/animals" replace />} />
      <Route path="/animals-data/:id" element={<Navigate to="/panel/animals" replace />} />

    </Routes>
  )
}

export default App
