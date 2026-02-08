export type Animal = {
  id: number
  animalId: string

  name: string
  species: string
  breed: string

  sex: string
  age: string

  coatColor: string
  weight: number

  identifyingMarks?: string | null
  shelterStatus: string
  adoptionStatus: string

  birthDate?: Date | null
  lastMeasured?: Date | null

  behavioralTags: string[]
  transponderNumber?: string | null
  microchippingDate?: Date | null
}
