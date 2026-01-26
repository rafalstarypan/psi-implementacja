import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import apiClient from '@/api/client'
import { useAuth } from '@/features/auth/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  ArrowLeft,
  Package,
  Plus,
  Minus,
  Calendar,
  AlertCircle,
  TrendingUp,
  TrendingDown,
} from 'lucide-react'

interface InventoryLog {
  id: number
  operation_type: 'IN' | 'OUT'
  operation_type_display: string
  quantity: number
  comment: string
  timestamp: string
  performed_by: { id: number; email: string; full_name: string } | null
}

interface UnitOfMeasure {
  id: number
  name: string
  abbreviation: string
}

interface PendingOrder {
  id: number
  supplier_name: string
  quantity: number
  expected_delivery_date: string
  status: string
  status_display: string
}

interface SupplyItemDetailType {
  id: number
  name: string
  description: string
  category: { id: number; name: string }
  current_quantity: number
  min_stock: number
  unit: UnitOfMeasure
  stock_status: 'good' | 'warning' | 'low'
  pending_orders: PendingOrder[]
  recent_logs: InventoryLog[]
}

const stockStatusConfig = {
  good: { label: 'Stan dobry', variant: 'default' as const },
  warning: { label: 'Wymaga uzupełnienia', variant: 'secondary' as const },
  low: { label: 'Niski stan', variant: 'secondary' as const },
}

export function SupplyItemDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [changeType, setChangeType] = useState<'in' | 'out'>('in')
  const [quantity, setQuantity] = useState('')
  const [reason, setReason] = useState('')

  const canModify = user?.role === 'employee' || user?.role === 'volunteer'

  const {
    data: item,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['supplyItem', id],
    queryFn: async () => {
      const response = await apiClient.get(`/supplies/items/${id}/`)
      return response.data as SupplyItemDetailType
    },
  })

  const updateInventoryMutation = useMutation({
    mutationFn: async (data: {
      change_type: string
      quantity_change: number
      reason: string
    }) => {
      return apiClient.post(`/supplies/items/${id}/update_inventory/`, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['supplyItem', id] })
      queryClient.invalidateQueries({ queryKey: ['supplies'] })
      setIsDialogOpen(false)
      setQuantity('')
      setReason('')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const qty = parseInt(quantity)
    if (isNaN(qty) || qty <= 0) return

    updateInventoryMutation.mutate({
      change_type: changeType,
      quantity_change: qty,
      reason,
    })
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  }

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Ładowanie...</div>
      </div>
    )
  }

  if (error || !item) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-red-600">
          Błąd podczas ładowania danych. Produkt nie został znaleziony.
        </CardContent>
      </Card>
    )
  }

  const statusConfig = stockStatusConfig[item.stock_status] || stockStatusConfig.good
  const unitAbbreviation = item.unit?.abbreviation || ''
  const isBelowMinimum = item.stock_status !== 'good'
  const inProgressOrders = item.pending_orders?.filter((o) => o.status === 'IN_PROGRESS') || []

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Button variant="ghost" onClick={() => navigate('/panel/supplies')}>
        <ArrowLeft className="w-4 h-4 mr-2" />
        Powrót do listy
      </Button>

      {/* Header Card */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <Package className="w-8 h-8 text-blue-600" />
              <div>
                <CardTitle>{item.name}</CardTitle>
                <CardDescription>{item.description}</CardDescription>
              </div>
            </div>
            <Badge variant="outline">{item.category.name}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Current Stock */}
            <div className="space-y-2">
              <div className="text-sm text-gray-500">Aktualny stan</div>
              <div className="text-3xl tabular-nums">
                {item.current_quantity}
                <span className="text-lg text-gray-500 ml-2">{unitAbbreviation}</span>
              </div>
            </div>

            {/* Min Stock */}
            <div className="space-y-2">
              <div className="text-sm text-gray-500">Minimalny stan</div>
              <div className="text-3xl tabular-nums">
                {item.min_stock}
                <span className="text-lg text-gray-500 ml-2">{unitAbbreviation}</span>
              </div>
            </div>

            {/* Status */}
            <div className="space-y-2">
              <div className="text-sm text-gray-500">Status</div>
              <Badge variant={statusConfig.variant} className="text-base px-3 py-1">
                {statusConfig.label}
              </Badge>
            </div>
          </div>

          {/* Low Stock Warning */}
          {isBelowMinimum && (
            <div className="mt-6 flex items-center gap-2 text-sm text-orange-600">
              <AlertCircle className="w-4 h-4" />
              <span>Stan magazynowy poniżej minimum</span>
            </div>
          )}

          {/* Quick Actions */}
          {canModify && (
            <div className="flex gap-3 pt-6 mt-6 border-t">
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button onClick={() => setChangeType('in')}>
                    <Plus className="h-4 w-4 mr-2" />
                    Przyjęcie towaru
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <form onSubmit={handleSubmit}>
                    <DialogHeader>
                      <DialogTitle>
                        {changeType === 'in' ? 'Przyjęcie towaru' : 'Wydanie towaru'}
                      </DialogTitle>
                      <DialogDescription>
                        {item.name} - aktualna ilość: {item.current_quantity} {unitAbbreviation}
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="change-type">Typ operacji</Label>
                        <Select
                          value={changeType}
                          onValueChange={(v) => setChangeType(v as 'in' | 'out')}
                        >
                          <SelectTrigger id="change-type">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="in">Przyjęcie (PZ)</SelectItem>
                            <SelectItem value="out">Wydanie (WZ)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="quantity">Ilość ({unitAbbreviation})</Label>
                        <Input
                          id="quantity"
                          type="number"
                          min="1"
                          value={quantity}
                          onChange={(e) => setQuantity(e.target.value)}
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="reason">Powód / Uwagi</Label>
                        <Textarea
                          id="reason"
                          value={reason}
                          onChange={(e) => setReason(e.target.value)}
                          placeholder="Opcjonalny opis operacji..."
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                        Anuluj
                      </Button>
                      <Button type="submit" disabled={updateInventoryMutation.isPending}>
                        {updateInventoryMutation.isPending ? 'Zapisywanie...' : 'Zapisz'}
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>

              <Button
                variant="outline"
                onClick={() => {
                  setChangeType('out')
                  setIsDialogOpen(true)
                }}
              >
                <Minus className="h-4 w-4 mr-2" />
                Wydanie towaru
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pending Orders */}
      {inProgressOrders.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Oczekujące dostawy</CardTitle>
            <CardDescription>Zamówienia w trakcie realizacji</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {inProgressOrders.map((order) => (
                <div
                  key={order.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span>Oczekiwana dostawa: {formatDate(order.expected_delivery_date)}</span>
                    </div>
                    <div className="text-sm text-gray-500">Dostawca: {order.supplier_name}</div>
                  </div>
                  <div className="text-right">
                    <div className="tabular-nums">
                      {order.quantity} {unitAbbreviation}
                    </div>
                    <Badge variant="outline" className="mt-1">
                      W realizacji
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Inventory History */}
      <Card>
        <CardHeader>
          <CardTitle>Historia operacji magazynowych</CardTitle>
          <CardDescription>Rejestr wszystkich operacji przyjęcia i wydania towaru</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg">
            {!item.recent_logs || item.recent_logs.length === 0 ? (
              <div className="py-8 text-center text-gray-500">Brak zapisów w historii</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data i godzina</TableHead>
                    <TableHead>Typ operacji</TableHead>
                    <TableHead>Ilość</TableHead>
                    <TableHead>Powód</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {item.recent_logs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="tabular-nums">{formatDateTime(log.timestamp)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {log.operation_type === 'IN' ? (
                            <>
                              <TrendingUp className="w-4 h-4 text-green-600" />
                              <Badge
                                variant="outline"
                                className="text-green-600 border-green-600"
                              >
                                Przyjęcie
                              </Badge>
                            </>
                          ) : (
                            <>
                              <TrendingDown className="w-4 h-4 text-red-600" />
                              <Badge variant="outline" className="text-red-600 border-red-600">
                                Wydanie
                              </Badge>
                            </>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="tabular-nums">
                        <span className={log.operation_type === 'IN' ? 'text-green-600' : 'text-red-600'}>
                          {log.operation_type === 'IN' ? '+' : '-'}
                          {log.quantity} {unitAbbreviation}
                        </span>
                      </TableCell>
                      <TableCell>{log.comment || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
