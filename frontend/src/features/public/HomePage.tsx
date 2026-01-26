import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/features/auth/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Heart, PawPrint, Users, Shield, LogOut } from 'lucide-react'

export function HomePage() {
  const navigate = useNavigate()
  const { isAuthenticated, user, logout } = useAuth()

  const canAccessPanel = user?.role === 'employee'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <PawPrint className="w-8 h-8 text-primary" />
            <span className="text-xl font-bold">Schronisko dla Zwierząt</span>
          </div>
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <span className="text-sm text-gray-600">
                  Zalogowano jako: {user?.full_name}
                </span>
                {canAccessPanel && (
                  <Button onClick={() => navigate('/panel/supplies')}>
                    Panel pracownika
                  </Button>
                )}
                <Button variant="outline" onClick={logout}>
                  <LogOut className="w-4 h-4 mr-2" />
                  Wyloguj
                </Button>
              </>
            ) : (
              <Button onClick={() => navigate('/login')}>
                Zaloguj się
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-gray-900 to-gray-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <Heart className="w-16 h-16 mx-auto mb-6 text-red-400" />
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Witaj w Schronisku dla Zwierząt
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Pomagamy bezdomnym zwierzętom znaleźć kochające domy.
            Każde zwierzę zasługuje na drugą szansę.
          </p>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">150+</div>
              <div className="text-gray-600">Zwierząt pod opieką</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">500+</div>
              <div className="text-gray-600">Udanych adopcji</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">50+</div>
              <div className="text-gray-600">Wolontariuszy</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">15</div>
              <div className="text-gray-600">Lat doświadczenia</div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Co oferujemy</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <Heart className="w-10 h-10 text-red-500 mb-2" />
                <CardTitle>Adopcja zwierząt</CardTitle>
                <CardDescription>
                  Pomagamy znaleźć idealnego towarzysza dla Twojej rodziny
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Wszystkie nasze zwierzęta są zaszczepione, odrobaczone i zaczipowane.
                  Przeprowadzamy rozmowy adopcyjne, aby zapewnić najlepsze dopasowanie.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Shield className="w-10 h-10 text-blue-500 mb-2" />
                <CardTitle>Opieka weterynaryjna</CardTitle>
                <CardDescription>
                  Profesjonalna opieka medyczna dla wszystkich podopiecznych
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Współpracujemy z doświadczonymi weterynarzami, którzy zapewniają
                  kompleksową opiekę zdrowotną naszym zwierzętom.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Users className="w-10 h-10 text-green-500 mb-2" />
                <CardTitle>Wolontariat</CardTitle>
                <CardDescription>
                  Dołącz do naszego zespołu wolontariuszy
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Szukamy osób, które chcą poświęcić swój czas na pomoc zwierzętom.
                  Każda para rąk jest na wagę złota!
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <PawPrint className="w-6 h-6" />
            <span className="font-semibold">Schronisko dla Zwierząt</span>
          </div>
          <p className="text-gray-400 text-sm">
            © 2024 Schronisko dla Zwierząt. Wszelkie prawa zastrzeżone.
          </p>
        </div>
      </footer>
    </div>
  )
}
