import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select"

type SourceType = "person" | "institution" | "unknown"
type Mode = "existing" | "new"

export type IntakeSourcePayload = {
  source_type: "person" | "institution"
  source: Record<string, any>
}

type Props = {
  onChange: (value: IntakeSourcePayload | null) => void
}

export function IntakeSourceSelector({ onChange }: Props) {
  const [sourceType, setSourceType] = useState<SourceType | "">("")
  const [mode, setMode] = useState<Mode>("existing")
  const [existingId, setExistingId] = useState("")

  const [person, setPerson] = useState({
    firstname: "",
    email_address: "",
    phone_number: "",
    address: {
      city: "",
      postal_code: "",
      street: "",
      building_number: "",
      apartment_number: "",
    },
  })

  useEffect(() => {
    // nothing selected yet
    if (!sourceType) {
      onChange(null)
      return
    }

    // UNKNOWN → institution + id = null
    if (sourceType === "unknown") {
      onChange({
        source_type: "institution",
        source: { id: null },
      })
      return
    }

    // EXISTING SOURCE
    if (mode === "existing") {
      if (!existingId.trim()) {
        onChange(null)
        return
      }

      onChange({
        source_type: sourceType,
        source: { id: existingId },
      })
      return
    }

    // NEW PERSON / INSTITUTION
    onChange({
      source_type: sourceType,
      source: person,
    })
  }, [sourceType, mode, existingId, person, onChange])

  return (
    <div className="space-y-4">
      {/* Source Type */}
      <div className="grid gap-2">
        <Label>Source Type *</Label>
        <Select value={sourceType} onValueChange={setSourceType}>
          <SelectTrigger>
            <SelectValue placeholder="Select source type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="person">Person</SelectItem>
            <SelectItem value="institution">Institution</SelectItem>
            <SelectItem value="unknown">Unknown</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* UNKNOWN */}
      {sourceType === "unknown" && (
        <p className="text-sm text-muted-foreground">
          Source will be saved as <b>institution / not known</b>
        </p>
      )}

      {/* PERSON / INSTITUTION */}
      {sourceType && sourceType !== "unknown" && (
        <>
          {/* Mode */}
          <div className="grid gap-2">
            <Label>Source Mode *</Label>
            <Select value={mode} onValueChange={setMode}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="existing">Use existing</SelectItem>
                <SelectItem value="new">Create new</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Existing ID */}
          {mode === "existing" && (
            <div className="grid gap-2">
              <Label>Source ID *</Label>
              <Input
                value={existingId}
                onChange={(e) => setExistingId(e.target.value)}
                placeholder="Enter source ID"
              />
            </div>
          )}

          {/* New Person / Institution */}
          {mode === "new" && (
            <div className="grid gap-3 border rounded p-3">
              <Label>Create new {sourceType}</Label>

              <Input
                placeholder="First name"
                value={person.firstname}
                onChange={(e) =>
                  setPerson({ ...person, firstname: e.target.value })
                }
              />

              <Input
                placeholder="Email"
                value={person.email_address}
                onChange={(e) =>
                  setPerson({ ...person, email_address: e.target.value })
                }
              />

              <Input
                placeholder="Phone number"
                value={person.phone_number}
                onChange={(e) =>
                  setPerson({ ...person, phone_number: e.target.value })
                }
              />

              <div className="grid grid-cols-2 gap-2">
                <Input
                  placeholder="City"
                  value={person.address.city}
                  onChange={(e) =>
                    setPerson({
                      ...person,
                      address: { ...person.address, city: e.target.value },
                    })
                  }
                />
                <Input
                  placeholder="Postal code"
                  value={person.address.postal_code}
                  onChange={(e) =>
                    setPerson({
                      ...person,
                      address: {
                        ...person.address,
                        postal_code: e.target.value,
                      },
                    })
                  }
                />
                <Input
                  placeholder="Street"
                  value={person.address.street}
                  onChange={(e) =>
                    setPerson({
                      ...person,
                      address: { ...person.address, street: e.target.value },
                    })
                  }
                />
                <Input
                  placeholder="Building number"
                  value={person.address.building_number}
                  onChange={(e) =>
                    setPerson({
                      ...person,
                      address: {
                        ...person.address,
                        building_number: e.target.value,
                      },
                    })
                  }
                />
                <Input
                  placeholder="Apartment number"
                  value={person.address.apartment_number}
                  onChange={(e) =>
                    setPerson({
                      ...person,
                      address: {
                        ...person.address,
                        apartment_number: e.target.value,
                      },
                    })
                  }
                />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
