// features/animals/AnimalIntakes.tsx
import { useParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import apiClient from "@/api/client"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { CalendarIcon, MapPin, Heart, User, Building } from "lucide-react"
import { Person, Institution } from "./types"

interface Intake {
  intake_date: string
  intake_type: string
  animal_condition: string
  location: string
  source_type: "person" | "institution" | null
  source_id: string | null
}

interface IntakeResponse {
  count: number
  next: string | null
  previous: string | null
  results: Intake[]
}

export function AnimalIntakesPage() {
  const { id } = useParams<{ id: string }>()

  const { data, isLoading, error } = useQuery<IntakeResponse>({
    queryKey: ["animal-intakes", id],
    queryFn: async () => {
      const res = await apiClient.get(`/animals/${id}/intakes/`)
      return res.data
    },
  })

  if (isLoading) {
    return <div className="text-center py-12 text-gray-500">Loading intakes...</div>
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        Error loading intakes.
      </div>
    )
  }

  if (!data || data.results.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No intakes found for this animal.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {data.results.map((intake, idx) => (
        <IntakeCard key={idx} intake={intake} />
      ))}
    </div>
  )
}

function IntakeCard({ intake }: { intake: Intake }) {
  const { data: source, isLoading, error } = useQuery<Person | Institution | null>({
    queryKey: ["source-details", intake.source_type, intake.source_id],
    queryFn: async () => {
      if (!intake.source_id) return null;

      if (intake.source_type === "person") {
        const res = await apiClient.get<Person>(`/parties/persons/${intake.source_id}`);
        return res.data;
      }

      if (intake.source_type === "institution") {
        const res = await apiClient.get<Institution>(`/parties/institutions/${intake.source_id}`);
        return res.data;
      }

      return null;
    },
    enabled: !!intake.source_type && !!intake.source_id,
  });

  return (
    <Card className="bg-white">
      <CardHeader>
        <CardTitle>
          <CalendarIcon className="w-4 h-4 mr-2 inline" />
          {new Date(intake.intake_date).toLocaleDateString("pl-PL")}
        </CardTitle>
        <CardDescription>{intake.intake_type}</CardDescription>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
        <Info label="Condition" value={intake.animal_condition || "No data"} icon={<Heart className="w-4 h-4" />} />
        <Info label="Location" value={intake.location || "No data"} icon={<MapPin className="w-4 h-4" />} />

        <div className="col-span-1 md:col-span-2">
          <p className="text-gray-500 font-medium mb-1">Source info:</p>

          {isLoading && <p className="text-gray-400">Loading source details...</p>}
          {error && <p className="text-red-600">Error loading source details.</p>}
          {!intake.source_id && <p className="text-gray-400">Source details are unknown</p>}

          {source && intake.source_type === "person" && (
            <div className="ml-2">
              <p>
                <User className="inline w-4 h-4 mr-1" />
                {source.firstname} {source.lastname}
              </p>
              <p>Phone: {source.phone_number || "No data"}</p>
              <p>Email: {source.email_address || "No data"}</p>
              <p>
                Address: {source.address?.street || "No data"} {source.address?.building_number || ""}
                {source.address?.apartment_number ? `/${source.address.apartment_number}` : ""},{" "}
                {source.address?.postal_code || ""} {source.address?.city || ""}
              </p>
            </div>
          )}

          {source && intake.source_type === "institution" && (
            <div className="ml-2">
              <p>
                <Building className="inline w-4 h-4 mr-1" />
                {source.name || "No data"}
              </p>
              <p>Phone: {source.phone_number || "No data"}</p>
              <p>Email: {source.email_address || "No data"}</p>
              <p>
                Address: {source.address?.street || "No data"} {source.address?.building_number || ""}
                {source.address?.apartment_number ? `/${source.address.apartment_number}` : ""},{" "}
                {source.address?.postal_code || ""} {source.address?.city || ""}
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}


function Info({ label, value, icon }: { label: string; value: string | null | undefined; icon?: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2">
      {icon}
      <span className="text-gray-500">{label}:</span>
      <span className="font-medium">{value || "No data"}</span>
    </div>
  )
}
