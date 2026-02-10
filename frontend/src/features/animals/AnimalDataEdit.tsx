import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { useQuery, useMutation } from "@tanstack/react-query"
import { toast } from "sonner"

import apiClient from "@/api/client"
import { Animal, Tag, tagsFromApi } from "./types"
import { mapAnimalFromApi } from "./animal.mapper"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { AsyncParentSelect } from "./animalNameLookup"

export function AnimalDataEdit() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: animal, isLoading } = useQuery<Animal>({
    queryKey: ["animal", id],
    queryFn: async () => {
      const res = await apiClient.get(`/animals/${id}/`)
      return mapAnimalFromApi(res.data)
    },
    enabled: !!id,
  })

  const [form, setForm] = useState<Partial<Animal>>({})

  /** initialize form once animal is loaded */
  useEffect(() => {
    if (animal) {
      setForm({
        ...animal,
        behavioralTags: animal.behavioralTags ?? [],
      })
    }
  }, [animal])

  const updateMutation = useMutation({
    mutationFn: async () => {
      return apiClient.patch(`/animals/${id}/`, {
        name: form.name,
        species: form.species,
        breed: form.breed,
        sex: form.sex,
        birth_date: form.birthDate,
        coat_color: form.coatColor,
        weight: form.weight,
        identifying_marks: form.identifyingMarks,
        transponder_number: form.transponderNumber,
        microchipping_date: form.microchippingDate,
        behavioral_tags: form.behavioralTags,
        last_measured: form.lastMeasured,
        parents: form.parents,
        status: form.shelterStatus,
      })
    },
    onSuccess: () => {
      navigate(`/panel/animals-data/${id}`)
    },
onError: (error: any) => {
  const data = error.response?.data

  const message =
    typeof data === "string"
      ? data
      : formatApiError(data) ||
        "Failed to update animal. Please check your input."

  toast.error("Validation error", {
    description: message,
  })
},})

  if (isLoading || !animal) {
    return <div className="py-10 text-center">Loading…</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-5xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Edit animal</h1>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate(-1)}>
              Cancel
            </Button>
            <Button onClick={() => updateMutation.mutate()}>
              Save changes
            </Button>
          </div>
        </div>

        {/* Basic info */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>Edit core animal data</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">

            <InputField
              label="Name"
              value={form.name ?? ""}
              onChange={(v) => setForm({ ...form, name: v })}
            />

            <InputField
              label="Breed"
              value={form.breed ?? ""}
              onChange={(v) => setForm({ ...form, breed: v })}
            />

            <SelectField
              label="Species"
              value={form.species ?? ""}
              onChange={(v) => setForm({ ...form, species: v })}
              options={[
                { value: "DOG", label: "Dog" },
                { value: "CAT", label: "Cat" },
                { value: "OTHER", label: "Other" },
              ]}
            />

            <SelectField
              label="Sex"
              value={form.sex ?? ""}
              onChange={(v) => setForm({ ...form, sex: v })}
              options={[
                { value: "MALE", label: "Male" },
                { value: "FEMALE", label: "Female" },
              ]}
            />

            <InputField
              label="Birth date"
              type="date"
              value={form.birthDate ?? ""}
              onChange={(v) => setForm({ ...form, birthDate: v || null})}
            />

        <InputField
          label="Transponder number"
          value={form.transponderNumber ?? ""}
          onChange={(v) => setForm({ ...form, transponderNumber: v || null })}
        />

               <InputField
         label="Microchipping date"
         type="date"
         value={form.microchippingDate ?? ""}
         onChange={(v) => setForm({ ...form, microchippingDate: v || null })}
/>

<AsyncParentSelect
  label="Parents"
  value={form.parents ?? []}          // ["CAT-002", "CAT-005"]
  onChange={(animalIds) => setForm({ ...form, parents: animalIds })}
/>


<div className="flex flex-col gap-2">
  <Label>Shelter status</Label>

  <Select
    value={form.shelterStatus}
    onValueChange={(v) =>
      setForm({ ...form, shelterStatus: v })
    }
  >
    <SelectTrigger>
      <SelectValue />
    </SelectTrigger>

    <SelectContent>
      <SelectItem value="NEW_INTAKE">New intake</SelectItem>
      <SelectItem value="IN_SHELTER">In shelter</SelectItem>
      <SelectItem value="QUARANTINE">Quarantine</SelectItem>
      <SelectItem value="MEDICAL_TREATMENT">Medical treatment</SelectItem>
      <SelectItem value="ADOPTED">Adopted</SelectItem>
      <SelectItem value="DECEASED">Deceased</SelectItem>
    </SelectContent>
  </Select>
</div>





          </CardContent>
        </Card>

        {/* Appearance */}
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">

            <InputField
              label="Coat color"
              value={form.coatColor ?? ""}
              onChange={(v) => setForm({ ...form, coatColor: v })}
            />

            <InputField
              label="Weight (kg)"
              type="number"
              value={form.weight?.toString() ?? ""}
              onChange={(v) => setForm({ ...form, weight: Number(v) })}
            />

                           <InputField
         label="Last measured"
         type="date"
         value={form.lastMeasured ?? ""}
         onChange={(v) => setForm({ ...form, lastMeasured: v || null })}
/>

            <TextareaField
              label="Identifying marks"
              value={form.identifyingMarks ?? ""}
              onChange={(v) => setForm({ ...form, identifyingMarks: v })}
            />
          </CardContent>
        </Card>

        {/* Behavior */}
        <Card>
          <CardHeader>
            <CardTitle>Behavior</CardTitle>
          </CardHeader>
          <CardContent>
          <MultiTagSelect
            label="Behavioral tags"
            options={tagsFromApi}
            value={form.behavioralTags ?? []}
            onChange={(ids) =>
              setForm({
                ...form,
                behavioralTags: ids,
              })
            }
          />

          </CardContent>
        </Card>

      </div>
    </div>
  )

}


function InputField({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string
  value: string
  type?: string
  onChange: (v: string) => void
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm text-gray-500">{label}</label>
      <Input type={type} value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  )
}

function TextareaField({
  label,
  value,
  onChange,
}: {
  label: string
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm text-gray-500">{label}</label>
      <Textarea value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  )
}


function SelectField({
  label,
  value,
  onChange,
  options,
}: {
  label: string
  value: string
  onChange: (v: string) => void
  options: { value: string; label: string }[]
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm text-gray-500">{label}</label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              {opt.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}


function formatApiError(data: any): string {
  if (!data || typeof data !== "object") return String(data)

  return Object.entries(data)
    .map(([field, messages]) => {
      if (Array.isArray(messages)) {
        return `${field}: ${messages.join(", ")}`
      }
      return `${field}: ${messages}`
    })
    .join("\n\n")
}

type Props = {
  label: string
  options: Tag[]
  value: number[]
  onChange: (value: number[]) => void
}


export function MultiTagSelect({
  label,
  options,
  value,
  onChange,
}: Props) {
  const toggle = (id: number) => {
    onChange(
      value.includes(id)
        ? value.filter((v) => v !== id)
        : [...value, id]
    )
  }

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">{label}</label>

      <div className="border rounded-md p-3 space-y-2">
        {options.map((tag) => (
          <label
            key={tag.id}
            className="flex items-center gap-2 cursor-pointer"
          >
            <input
              type="checkbox"
              checked={value.includes(tag.id)}
              onChange={() => toggle(tag.id)}
            />
            <span className="text-sm">{tag.name}</span>
          </label>
        ))}
      </div>
    </div>
  )
}