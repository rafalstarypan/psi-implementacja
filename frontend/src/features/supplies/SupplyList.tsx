import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import apiClient from '@/api/client'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Package, Search, Calendar, AlertCircle } from 'lucide-react'

interface Category {
  id: number
  name: string
}

interface UnitOfMeasure {
  id: number
  name: string
  abbreviation: string
}

interface NextDelivery {
  expected_date: string
  supplier_name: string
  quantity: number
}

interface SupplyItem {
  id: number
  name: string
  description: string
  category: Category
  current_quantity: number
  min_stock: number
  unit: UnitOfMeasure
  stock_status: 'good' | 'warning' | 'low'
  next_delivery: NextDelivery | null
}

interface SupplyListResponse {
  count: number
  results: SupplyItem[]
}

const stockStatusConfig = {
  good: { label: 'Dobry', variant: 'default' as const },
  warning: { label: 'Uwaga', variant: 'secondary' as const },
  low: { label: 'Niski', variant: 'destructive' as const },
}

export function SupplyList() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['supplies', search],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (search) params.append('search', search)

      const response = await apiClient.get(`/supplies/items/?${params.toString()}`)
      return response.data as SupplyListResponse
    },
  })

  const supplies = data?.results || []

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  }

  const isDeliverySoon = (dateString: string) => {
    const deliveryDate = new Date(dateString)
    const today = new Date()
    const diffTime = deliveryDate.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays <= 3 && diffDays >= 0
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-red-600">
          Błąd podczas ładowania danych. Spróbuj odświeżyć stronę.
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-3">
        <Package className="w-8 h-8 text-blue-600" />
        <div>
          <h1 className="text-2xl font-bold">Stan Magazynu</h1>
          <p className="text-gray-600">Monitorowanie zasobów w magazynie schroniska</p>
        </div>
      </div>

      {/* Main Card */}
      <Card>
        <CardHeader>
          <CardTitle>Zasoby magazynowe</CardTitle>
          <CardDescription>
            Przeglądaj dostępne zasoby oraz sprawdzaj planowane dostawy
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Search */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <Input
                type="text"
                placeholder="Wyszukaj zasób po nazwie..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Table */}
          <div className="border rounded-lg">
            {isLoading ? (
              <div className="py-8 text-center text-gray-500">Ładowanie...</div>
            ) : supplies.length === 0 ? (
              <div className="py-8 text-center text-gray-500">
                Nie znaleziono zasobów pasujących do wyszukiwania
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nazwa zasobu</TableHead>
                    <TableHead>Kategoria</TableHead>
                    <TableHead>Ilość w magazynie</TableHead>
                    <TableHead>Stan</TableHead>
                    <TableHead>Następna dostawa</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {supplies.map((item) => {
                    const status = stockStatusConfig[item.stock_status] || stockStatusConfig.good
                    const deliverySoon = item.next_delivery
                      ? isDeliverySoon(item.next_delivery.expected_date)
                      : false

                    return (
                      <TableRow
                        key={item.id}
                        className="cursor-pointer hover:bg-gray-50"
                        onClick={() => navigate(`/panel/supplies/${item.id}`)}
                      >
                        <TableCell>
                          <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2">
                              <Package className="w-4 h-4 text-gray-400" />
                              <span className="text-blue-600 hover:underline">{item.name}</span>
                            </div>
                            <span className="text-sm text-gray-500 pl-6">{item.description}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{item.category?.name}</Badge>
                        </TableCell>
                        <TableCell>
                          <span className="tabular-nums">
                            {item.current_quantity} {item.unit?.abbreviation}
                          </span>
                        </TableCell>
                        <TableCell>
                          <Badge variant={status.variant}>{status.label}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-col gap-1">
                            {item.next_delivery ? (
                              <>
                                <div className="flex items-center gap-2">
                                  <Calendar className="w-4 h-4 text-gray-400" />
                                  <span className={deliverySoon ? 'text-orange-600' : ''}>
                                    {formatDate(item.next_delivery.expected_date)}
                                  </span>
                                  {deliverySoon && (
                                    <AlertCircle className="w-4 h-4 text-orange-600" />
                                  )}
                                </div>
                                <span className="text-sm text-gray-500">
                                  Dostawca: {item.next_delivery.supplier_name}
                                </span>
                              </>
                            ) : (
                              <span className="text-gray-500">Brak planowanej dostawy</span>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            )}
          </div>

          {/* Legend */}
          <div className="mt-6 flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span>Niski stan</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
              <span>Wymaga uzupełnienia</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gray-800 rounded-full"></div>
              <span>Stan dobry</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
