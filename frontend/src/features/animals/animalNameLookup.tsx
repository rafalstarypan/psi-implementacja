import { useState, useEffect } from "react"
import apiClient from "@/api/client"

type AnimalOption = { animal_id: string }

type Props = {
  label: string
  value: string[]           // now array of animal_id strings
  onChange: (ids: string[]) => void
}

export function AsyncParentSelect({ label, value, onChange }: Props) {
  const [query, setQuery] = useState("")
  const [options, setOptions] = useState<AnimalOption[]>([])

  const safeValue = value ?? []
  const safeOptions = options ?? []

  const add = (animal_id: string) => {
    if (!safeValue.includes(animal_id)) onChange([...safeValue, animal_id])
    setQuery("")
  }

  const remove = (animal_id: string) => {
    onChange(safeValue.filter((v) => v !== animal_id))
  }

  // search
  useEffect(() => {
    if (!query) return setOptions([])

    let active = true
    apiClient
      .get("/animals/", { params: { search: query } })
      .then((res) => {
        if (!active) return
        setOptions(res.data.results.map((a: any) => ({ animal_id: a.animal_id })))
      })

    return () => {
      active = false
    }
  }, [query])

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">{label}</label>

      <div className="flex flex-wrap gap-1">
        {safeValue.map((animal_id) => (
          <span
            key={animal_id}
            className="bg-gray-200 px-2 py-1 rounded text-sm cursor-pointer"
            onClick={() => remove(animal_id)}
          >
            {animal_id} ✕
          </span>
        ))}
      </div>

      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search animal by animal ID..."
        className="w-full border rounded px-3 py-2"
      />

      {query && (
        <div className="border rounded max-h-40 overflow-auto">
          {safeOptions.length === 0 && (
            <div className="p-2 text-sm text-muted-foreground">No results</div>
          )}
          {safeOptions.map((a) => (
            <div
              key={a.animal_id}
              className="p-2 hover:bg-gray-100 cursor-pointer text-sm"
              onClick={() => add(a.animal_id)}
            >
              {a.animal_id}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

