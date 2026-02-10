import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import apiClient from '@/api/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Search, Plus, Pencil } from 'lucide-react'

interface Animal {
  id: number
  animal_id: string
  name: string
  species: 'DOG' | 'CAT' | 'OTHER'
  species_display: string
  breed: string
  age_display: string
  sex: string
  sex_display: string
  status: string
  status_display: string
  intake_date: string
}

interface AnimalListResponse {
  count: number
  results: Animal[]
}

const shelterStatusVariants: Record<string, 'default' | 'outline'> = {
  NEW_INTAKE: 'outline',
  IN_SHELTER: 'default',
  QUARANTINE: 'outline',
  MEDICAL_TREATMENT: 'default',
  ADOPTED: 'outline',
  DECEASED: 'outline',
}

const adoptionStatusMap: Record<string, { label: string; variant: 'default' | 'outline' }> = {
  NEW_INTAKE: { label: 'Unavailable', variant: 'outline' },
  IN_SHELTER: { label: 'Available', variant: 'default' },
  QUARANTINE: { label: 'Unavailable', variant: 'outline' },
  MEDICAL_TREATMENT: { label: 'Unavailable', variant: 'outline' },
  ADOPTED: { label: 'Adopted', variant: 'default' },
  DECEASED: { label: 'Unavailable', variant: 'outline' },
}

export function AnimalList() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [speciesFilter, setSpeciesFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const { data, isLoading, error } = useQuery({
    queryKey: ['animals', search, speciesFilter, statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (speciesFilter && speciesFilter !== 'all') params.append('species', speciesFilter)
      if (statusFilter && statusFilter !== 'all') params.append('status', statusFilter)

      const response = await apiClient.get(`/animals/?${params.toString()}`)
      return response.data as AnimalListResponse
    },
  })

  const animals = data?.results || []
  const totalCount = data?.count || 0

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
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">List of animals</h1>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add New Animal
        </Button>
      </div>

      {/* Filters Card */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={speciesFilter} onValueChange={setSpeciesFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="All Species" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Species</SelectItem>
                <SelectItem value="DOG">Dog</SelectItem>
                <SelectItem value="CAT">Cat</SelectItem>
                <SelectItem value="OTHER">Rabbit</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="NEW_INTAKE">New Intake</SelectItem>
                <SelectItem value="IN_SHELTER">In Shelter</SelectItem>
                <SelectItem value="QUARANTINE">Quarantine</SelectItem>
                <SelectItem value="MEDICAL_TREATMENT">Medical Treatment</SelectItem>
                <SelectItem value="ADOPTED">Adopted</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Table */}
          <div className="mt-6 border rounded-lg">
            {isLoading ? (
              <div className="py-8 text-center text-gray-500">Ładowanie...</div>
            ) : animals.length === 0 ? (
              <div className="py-8 text-center text-gray-500">
                No animals found matching the criteria
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Animal ID</TableHead>
                    <TableHead>Species</TableHead>
                    <TableHead>Breed</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Sex</TableHead>
                    <TableHead>Shelter Status</TableHead>
                    <TableHead>Adoption Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {animals.map((animal) => {
                    const adoptionStatus = adoptionStatusMap[animal.status] || {
                      label: 'Unknown',
                      variant: 'outline' as const,
                    }
                    return (
                      <TableRow
                        key={animal.id}
                        className="cursor-pointer hover:bg-muted/50"
                        onClick={() => navigate(`/panel/animals-medical/${animal.id}`)}
                      >
                        <TableCell className="font-mono text-sm">{animal.animal_id}</TableCell>
                        <TableCell className="text-blue-600">{animal.species_display}</TableCell>
                        <TableCell>{animal.breed || '-'}</TableCell>
                        <TableCell className="text-blue-600">{animal.name}</TableCell>
                        <TableCell>{animal.sex_display}</TableCell>
                        <TableCell>
                          <Badge variant={shelterStatusVariants[animal.status] || 'outline'}>
                            {animal.status_display}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={adoptionStatus.variant}>{adoptionStatus.label}</Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              navigate(`/panel/animals/${animal.id}`)
                            }}
                          >
                            <Pencil className="w-4 h-4 mr-1" />
                            Edit
                          </Button>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            )}
          </div>

          {/* Pagination */}
          {animals.length > 0 && (
            <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
              <div>
                Showing 1-{animals.length} of {totalCount} animals
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" disabled>
                  &lt; Previous
                </Button>
                <span className="px-2">Page 1 of 1</span>
                <Button variant="outline" size="sm" disabled>
                  Next &gt;
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
