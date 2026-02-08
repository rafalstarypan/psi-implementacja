import { Animal } from "./types"

export function mapAnimalFromApi(api: any): Animal {
  return {
    id: api.id,
    animalId: api.animal_id,

    name: api.name,
    species: api.species_display,
    breed: api.breed,

    sex: api.sex_display,
    age: api.age_display,

    coatColor: api.coat_color,
    weight: Number(api.weight),

    identifyingMarks: api.identifying_marks,
    shelterStatus: api.status_display,
    adoptionStatus: api.status_display,

    birthDate: api.birth_date ? new Date(api.birth_date) : null,
    lastMeasured: null,

    behavioralTags: api.behavioral_tags ?? [],
    transponderNumber: api.transponder_number,
    microchippingDate: api.microchipping_date ? new Date(api.microchipping_date) : null,
  }
}
