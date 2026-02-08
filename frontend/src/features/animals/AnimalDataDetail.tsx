import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { CalendarIcon, Edit, History } from "lucide-react"
import { format } from "date-fns"
import { useNavigate, useParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import apiClient from '@/api/client'
import { Animal } from "./types"
import { mapAnimalFromApi } from "./animal.mapper"

export function AnimalDataDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: animal, isLoading, isError } = useQuery<Animal>({
    queryKey: ["animal", id],
    queryFn: async () => {
      const res = await apiClient.get(`/animals/${id}/`)
      return mapAnimalFromApi(res.data)
    },
    enabled: !!id,
  })

  if (isLoading) {
    return <div className="text-center py-10">Loading animal data…</div>
  }

  if (isError || !animal) {
    return <div className="text-center py-10 text-red-500">Animal not found</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-5xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{animal.name}</h1>
            <p className="text-gray-600">
              {animal.species} • {animal.breed} • ID {animal.animalId}
            </p>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => navigate(`/panel/animals/${animal.animalId}/intakes`)}
            >
              <History className="h-4 w-4 mr-2" />
              Intakes history
            </Button>

            <Button
              onClick={() => navigate(`/panel/animals/${animal.animalId}/edit`)}
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit info
            </Button>
          </div>
        </div>

        {/* Basic info */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>Core details about the animal</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <Info label="Species" value={animal.species} />
            <Info label="Breed" value={animal.breed} />
            <Info label="Sex" value={animal.sex} />
            <Info label="Age" value={`${animal.age} years`} />
            <Info label="Shelter status" value={animal.shelterStatus} />
            <Info label="Adoption status" value={animal.adoptionStatus} />
            <Info label="Transponder number" value={animal.transponderNumber ? animal.transponderNumber : "No transponder"} />
            <Info label="Microchipping date" value={animal.microchippingDate ? format(new Date(animal.microchippingDate), "PPP") : "Not microchipped"} />

            {animal.birthDate && (
              <Info
                label="Birth date"
                value={format(new Date(animal.birthDate), "PPP")}
                icon={<CalendarIcon className="h-4 w-4" />}
              />
            )}


          </CardContent>
        </Card>

        {/* Identifying marks */}
        {animal.identifyingMarks && (
          <Card>
            <CardHeader>
              <CardTitle>Appearance</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <Info label="Identifying marks" value={animal.identifyingMarks} />
            <Info label="Coat color" value={animal.coatColor} />
            <Info label="Weight" value={`${animal.weight} kg`} />
            {animal.lastMeasured && (
              <Info
                label="Last measured"
                value={format(new Date(animal.lastMeasured), "PPP")}
                icon={<CalendarIcon className="h-4 w-4" />}
              />
            )}
            </CardContent>
          </Card>
        )}

        {/* Behavior */}
        <Card>
          <CardHeader>
            <CardTitle>Behavior</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {animal.behavioralTags.length ? (
                animal.behavioralTags.map(tag => (
                  <Badge key={tag} variant="secondary">{tag}</Badge>
                ))
              ) : (
                <p className="text-sm text-gray-400">No behavioral tags</p>
              )}
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  )
}

function Info({
  label,
  value,
  icon,
}: {
  label: string
  value: string | null | undefined
  icon?: React.ReactNode
}) {
  return (
    <div className="flex flex-col">
      <span className="text-gray-500">{label}</span>
      <span className="flex items-center gap-2 font-medium">
        {icon}
        {value ?? "No data"}
      </span>
    </div>
  )
}

