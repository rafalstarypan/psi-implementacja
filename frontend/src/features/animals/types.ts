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
  parents: string[]
}


export interface Address {
  address_id?: string
  city: string
  postal_code: string
  street: string
  building_number: string
  apartment_number?: string
}

export interface Person {
  person_id: string
  firstname: string
  lastname: string
  phone_number: string
  email_address: string
  address: Address
}

export interface Institution {
  institution_id: string
  name: string
  phone_number: string
  email_address: string
  address: Address
}