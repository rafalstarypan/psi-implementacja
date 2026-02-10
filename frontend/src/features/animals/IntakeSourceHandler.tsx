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

const emptyAddress = {
  city: "",
  postal_code: "",
  street: "",
  building_number: "",
  apartment_number: "",
}

export function IntakeSourceSelector({ onChange }: Props) {
  const [sourceType, setSourceType] = useState<SourceType | "">("")
  const [mode, setMode] = useState<Mode>("existing")
  const [existingId, setExistingId] = useState("")

  const [person, setPerson] = useState({
    firstname: "",
    lastname: "",
    email_address: "",
    phone_number: "",
    address: emptyAddress,
  })

  const [institution, setInstitution] = useState({
    name: "",
    email_address: "",
    phone_number: "",
    address: emptyAddress,
  })

  useEffect(() => {
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

    // NEW PERSON / INSTITUTION → WRAPPED IN data
    onChange({
      source_type: sourceType,
      source: {
        data: sourceType === "person" ? person : institution,
      },
    })
  }, [sourceType, mode, existingId, person, institution, onChange])

  return (
    <div className="space-y-4">
      {/* Source Type */}
      <div className="grid gap-2">
        <Label>Source Type *</Label>
        <Select value={sourceType} onValueChange={(v) => setSourceType(v as SourceType | "")}>
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
            <Select value={mode} onValueChange={(v) => setMode(v as Mode)}>
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

          {/* NEW PERSON */}
          {mode === "new" && sourceType === "person" && (
            <div className="grid gap-3 border rounded p-3">
              <Label>Create new person</Label>

              <Input
                placeholder="First name"
                value={person.firstname}
                onChange={(e) =>
                  setPerson({ ...person, firstname: e.target.value })
                }
              />

              <Input
                placeholder="Last name"
                value={person.lastname}
                onChange={(e) =>
                  setPerson({ ...person, lastname: e.target.value })
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

              <AddressFields
                address={person.address}
                onChange={(address) =>
                  setPerson({ ...person, address })
                }
              />
            </div>
          )}

          {/* NEW INSTITUTION */}
          {mode === "new" && sourceType === "institution" && (
            <div className="grid gap-3 border rounded p-3">
              <Label>Create new institution</Label>

              <Input
                placeholder="Institution name"
                value={institution.name}
                onChange={(e) =>
                  setInstitution({ ...institution, name: e.target.value })
                }
              />

              <Input
                placeholder="Email"
                value={institution.email_address}
                onChange={(e) =>
                  setInstitution({
                    ...institution,
                    email_address: e.target.value,
                  })
                }
              />

              <Input
                placeholder="Phone number"
                value={institution.phone_number}
                onChange={(e) =>
                  setInstitution({
                    ...institution,
                    phone_number: e.target.value,
                  })
                }
              />

              <AddressFields
                address={institution.address}
                onChange={(address) =>
                  setInstitution({ ...institution, address })
                }
              />
            </div>
          )}
        </>
      )}
    </div>
  )
}

/* ---------------- Address subcomponent ---------------- */

type AddressProps = {
  address: typeof emptyAddress
  onChange: (address: typeof emptyAddress) => void
}

function AddressFields({ address, onChange }: AddressProps) {
  return (
    <div className="grid grid-cols-2 gap-2">
      <Input
        placeholder="City"
        value={address.city}
        onChange={(e) =>
          onChange({ ...address, city: e.target.value })
        }
      />
      <Input
        placeholder="Postal code"
        value={address.postal_code}
        onChange={(e) =>
          onChange({ ...address, postal_code: e.target.value })
        }
      />
      <Input
        placeholder="Street"
        value={address.street}
        onChange={(e) =>
          onChange({ ...address, street: e.target.value })
        }
      />
      <Input
        placeholder="Building number"
        value={address.building_number}
        onChange={(e) =>
          onChange({ ...address, building_number: e.target.value })
        }
      />
      <Input
        placeholder="Apartment number"
        value={address.apartment_number}
        onChange={(e) =>
          onChange({ ...address, apartment_number: e.target.value })
        }
      />
    </div>
  )
}
