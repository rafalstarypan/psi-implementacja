import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import apiClient from '@/api/client'
import { useAuth } from '@/features/auth/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, Pill, Syringe, Scissors, ChevronDown, ChevronUp } from 'lucide-react'

interface Medication {
  id: number
  medication_name: string
  dosage: string
  frequency: string
  start_date: string
  end_date: string | null
  prescribed_by_name: string
  notes: string
  is_active: boolean
}

interface Vaccination {
  id: number
  vaccine_name: string
  vaccination_date: string
  next_due_date: string | null
  administered_by_name: string
  batch_number: string
  notes: string
}

interface MedicalProcedure {
  id: number
  procedure_name: string
  procedure_date: string
  performed_by_name: string
  description: string
  outcome: string
  follow_up_required: boolean
  follow_up_date: string | null
}

interface AnimalDetail {
  id: number
  animal_id: string
  name: string
  species: 'DOG' | 'CAT' | 'OTHER'
  species_display: string
  breed: string
  age_display: string
  birth_date: string | null
  sex: string
  sex_display: string
  weight: number | null
  transponder_number: string | null
  status: string
  status_display: string
  intake_date: string
  notes: string
  medications: Medication[]
  vaccinations: Vaccination[]
  medical_procedures: MedicalProcedure[]
}

interface Veterinarian {
  id: number
  full_name: string
  email: string
}

export function AnimalMedicalRecord() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const [activeTab, setActiveTab] = useState('medication')
  const [showRecords, setShowRecords] = useState(false)

  // Medication form state
  const [medForm, setMedForm] = useState({
    medication_name: '',
    dosage: '',
    frequency: '',
    start_date: '',
    end_date: '',
    performed_by: '',
    reason: '',
    notes: '',
  })

  // Vaccination form state
  const [vaccinationForm, setVaccinationForm] = useState({
    vaccine_name: '',
    vaccine_for: '',
    vaccine_batch_number: '',
    vaccination_date: '',
    expiration_date: '',
    next_due_date: '',
    performed_by: '',
  })

  // Procedure form state
  const [procedureForm, setProcedureForm] = useState({
    procedure_date: '',
    performed_by: '',
    description: '',
    result: '',
    cost: '',
    notes: '',
  })

  const canModify = user?.role === 'employee'

  const { data: animal, isLoading, error } = useQuery({
    queryKey: ['animal', id],
    queryFn: async () => {
      const response = await apiClient.get(`/animals/${id}/`)
      return response.data as AnimalDetail
    },
  })

  const { data: veterinarians = [] } = useQuery({
    queryKey: ['veterinarians'],
    queryFn: async () => {
      const response = await apiClient.get('/animals/veterinarians/')
      return response.data as Veterinarian[]
    },
  })

  const addMedicationMutation = useMutation({
    mutationFn: async (data: typeof medForm) => {
      return apiClient.post(`/animals/${id}/medications/`, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['animal', id] })
      setMedForm({
        medication_name: '',
        dosage: '',
        frequency: '',
        start_date: '',
        end_date: '',
        performed_by: '',
        reason: '',
        notes: '',
      })
    },
  })

  const addVaccinationMutation = useMutation({
    mutationFn: async (data: typeof vaccinationForm) => {
      return apiClient.post(`/animals/${id}/vaccinations/`, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['animal', id] })
      setVaccinationForm({
        vaccine_name: '',
        vaccine_for: '',
        vaccine_batch_number: '',
        vaccination_date: '',
        expiration_date: '',
        next_due_date: '',
        performed_by: '',
      })
    },
  })

  const addProcedureMutation = useMutation({
    mutationFn: async (data: typeof procedureForm) => {
      return apiClient.post(`/animals/${id}/procedures/`, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['animal', id] })
      setProcedureForm({
        procedure_date: '',
        performed_by: '',
        description: '',
        result: '',
        cost: '',
        notes: '',
      })
    },
  })

  const handleMedicationSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    addMedicationMutation.mutate(medForm)
  }

  const handleVaccinationSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    addVaccinationMutation.mutate(vaccinationForm)
  }

  const handleProcedureSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    addProcedureMutation.mutate(procedureForm)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Ładowanie...</div>
      </div>
    )
  }

  if (error || !animal) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-red-600">
          Błąd podczas ładowania danych. Zwierzę nie zostało znalezione.
        </CardContent>
      </Card>
    )
  }

  const totalRecords =
    animal.medications.length + animal.vaccinations.length + animal.medical_procedures.length

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/panel/animals')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Powrót do listy
        </Button>
      </div>

      {/* Animal Info Card */}
      <Card>
        <CardHeader>
          <CardTitle>Zwierzę: {animal.name}</CardTitle>
          <CardDescription>
            {animal.species_display} • Płeć: {animal.sex_display} • Data urodzenia:{' '}
            {animal.birth_date
              ? new Date(animal.birth_date).toLocaleDateString('pl-PL')
              : 'Nieznana'}
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Main Input Forms */}
      {canModify && (
        <Card>
          <CardHeader>
            <CardTitle>Wprowadzanie danych medycznych</CardTitle>
            <CardDescription>
              Wypełnij formularz, aby dodać informacje o lekach, szczepieniach lub przeprowadzonych
              zabiegach
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-3 mb-6">
                <TabsTrigger value="medication" className="flex items-center gap-2">
                  <Pill className="w-4 h-4" />
                  Przepisane leki
                </TabsTrigger>
                <TabsTrigger value="vaccination" className="flex items-center gap-2">
                  <Syringe className="w-4 h-4" />
                  Szczepienia
                </TabsTrigger>
                <TabsTrigger value="procedure" className="flex items-center gap-2">
                  <Scissors className="w-4 h-4" />
                  Przeprowadzone zabiegi
                </TabsTrigger>
              </TabsList>

              {/* MEDICATION FORM */}
              <TabsContent value="medication">
                <form onSubmit={handleMedicationSubmit} className="space-y-6">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="med-name">Nazwa leku *</Label>
                        <Input
                          id="med-name"
                          value={medForm.medication_name}
                          onChange={(e) =>
                            setMedForm({ ...medForm, medication_name: e.target.value })
                          }
                          placeholder="np. Amoxicylina"
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="dosage">Dawkowanie *</Label>
                        <Input
                          id="dosage"
                          value={medForm.dosage}
                          onChange={(e) => setMedForm({ ...medForm, dosage: e.target.value })}
                          placeholder="np. 250mg"
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="frequency">Częstotliwość podawania *</Label>
                      <Input
                        id="frequency"
                        value={medForm.frequency}
                        onChange={(e) => setMedForm({ ...medForm, frequency: e.target.value })}
                        placeholder="np. 2 razy dziennie, raz na 8 godzin"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="start-date">Data rozpoczęcia *</Label>
                        <Input
                          id="start-date"
                          type="date"
                          value={medForm.start_date}
                          onChange={(e) => setMedForm({ ...medForm, start_date: e.target.value })}
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="end-date">Data zakończenia *</Label>
                        <Input
                          id="end-date"
                          type="date"
                          value={medForm.end_date}
                          onChange={(e) => setMedForm({ ...medForm, end_date: e.target.value })}
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="med-vet">Weterynarz *</Label>
                      <Select
                        value={medForm.performed_by}
                        onValueChange={(value) => setMedForm({ ...medForm, performed_by: value })}
                        required
                      >
                        <SelectTrigger id="med-vet">
                          <SelectValue placeholder="Wybierz weterynarza" />
                        </SelectTrigger>
                        <SelectContent>
                          {veterinarians.map((vet) => (
                            <SelectItem key={vet.id} value={vet.id.toString()}>
                              {vet.full_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="med-reason">Powód *</Label>
                      <Input
                        id="med-reason"
                        value={medForm.reason}
                        onChange={(e) => setMedForm({ ...medForm, reason: e.target.value })}
                        placeholder="np. Infekcja bakteryjna, profilaktyka"
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="med-notes">Notatki dodatkowe</Label>
                      <Textarea
                        id="med-notes"
                        value={medForm.notes}
                        onChange={(e) => setMedForm({ ...medForm, notes: e.target.value })}
                        placeholder="np. Podawać z jedzeniem, unikać produktów mlecznych..."
                        rows={3}
                      />
                    </div>
                  </div>

                  <Separator />

                  <div className="flex justify-end">
                    <Button type="submit" size="lg" disabled={addMedicationMutation.isPending}>
                      {addMedicationMutation.isPending ? 'Zapisywanie...' : 'Zapisz wpis o leku'}
                    </Button>
                  </div>
                </form>
              </TabsContent>

              {/* VACCINATION FORM */}
              <TabsContent value="vaccination">
                <form onSubmit={handleVaccinationSubmit} className="space-y-6">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="vacc-name">Nazwa szczepionki *</Label>
                      <Input
                        id="vacc-name"
                        value={vaccinationForm.vaccine_name}
                        onChange={(e) =>
                          setVaccinationForm({ ...vaccinationForm, vaccine_name: e.target.value })
                        }
                        placeholder="np. Nobivac DHPPi, Rabies"
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="vacc-for">Przeciwko (chorobie) *</Label>
                      <Input
                        id="vacc-for"
                        value={vaccinationForm.vaccine_for}
                        onChange={(e) =>
                          setVaccinationForm({ ...vaccinationForm, vaccine_for: e.target.value })
                        }
                        placeholder="np. Wścieklizna, Parwowiroza, Nosówka psów"
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="vacc-batch">Numer partii szczepionki *</Label>
                      <Input
                        id="vacc-batch"
                        value={vaccinationForm.vaccine_batch_number}
                        onChange={(e) =>
                          setVaccinationForm({
                            ...vaccinationForm,
                            vaccine_batch_number: e.target.value,
                          })
                        }
                        placeholder="np. AB12345"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="vacc-start-date">Data szczepienia *</Label>
                        <Input
                          id="vacc-start-date"
                          type="date"
                          value={vaccinationForm.vaccination_date}
                          onChange={(e) =>
                            setVaccinationForm({
                              ...vaccinationForm,
                              vaccination_date: e.target.value,
                            })
                          }
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="vacc-exp-date">Data wygaśnięcia *</Label>
                        <Input
                          id="vacc-exp-date"
                          type="date"
                          value={vaccinationForm.expiration_date}
                          onChange={(e) =>
                            setVaccinationForm({
                              ...vaccinationForm,
                              expiration_date: e.target.value,
                            })
                          }
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="vacc-next-due">Data następnego szczepienia</Label>
                      <Input
                        id="vacc-next-due"
                        type="date"
                        value={vaccinationForm.next_due_date}
                        onChange={(e) =>
                          setVaccinationForm({ ...vaccinationForm, next_due_date: e.target.value })
                        }
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="vacc-vet">Weterynarz *</Label>
                      <Select
                        value={vaccinationForm.performed_by}
                        onValueChange={(value) =>
                          setVaccinationForm({ ...vaccinationForm, performed_by: value })
                        }
                        required
                      >
                        <SelectTrigger id="vacc-vet">
                          <SelectValue placeholder="Wybierz weterynarza" />
                        </SelectTrigger>
                        <SelectContent>
                          {veterinarians.map((vet) => (
                            <SelectItem key={vet.id} value={vet.id.toString()}>
                              {vet.full_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Separator />

                  <div className="flex justify-end">
                    <Button type="submit" size="lg" disabled={addVaccinationMutation.isPending}>
                      {addVaccinationMutation.isPending
                        ? 'Zapisywanie...'
                        : 'Zapisz wpis o szczepieniu'}
                    </Button>
                  </div>
                </form>
              </TabsContent>

              {/* PROCEDURE FORM */}
              <TabsContent value="procedure">
                <form onSubmit={handleProcedureSubmit} className="space-y-6">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="proc-date">Data zabiegu *</Label>
                      <Input
                        id="proc-date"
                        type="date"
                        value={procedureForm.procedure_date}
                        onChange={(e) =>
                          setProcedureForm({ ...procedureForm, procedure_date: e.target.value })
                        }
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="proc-vet">Weterynarz *</Label>
                      <Select
                        value={procedureForm.performed_by}
                        onValueChange={(value) =>
                          setProcedureForm({ ...procedureForm, performed_by: value })
                        }
                        required
                      >
                        <SelectTrigger id="proc-vet">
                          <SelectValue placeholder="Wybierz weterynarza" />
                        </SelectTrigger>
                        <SelectContent>
                          {veterinarians.map((vet) => (
                            <SelectItem key={vet.id} value={vet.id.toString()}>
                              {vet.full_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="proc-description">Opis zabiegu *</Label>
                      <Textarea
                        id="proc-description"
                        value={procedureForm.description}
                        onChange={(e) =>
                          setProcedureForm({ ...procedureForm, description: e.target.value })
                        }
                        placeholder="Szczegółowy opis przeprowadzonego zabiegu..."
                        rows={4}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="outcome">Wynik/Przebieg zabiegu *</Label>
                      <Textarea
                        id="outcome"
                        value={procedureForm.result}
                        onChange={(e) =>
                          setProcedureForm({ ...procedureForm, result: e.target.value })
                        }
                        placeholder="Jak przebiegł zabieg, rezultat..."
                        rows={3}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="cost">Koszt (PLN) *</Label>
                      <Input
                        id="cost"
                        type="number"
                        step="0.01"
                        min="0"
                        value={procedureForm.cost}
                        onChange={(e) =>
                          setProcedureForm({ ...procedureForm, cost: e.target.value })
                        }
                        placeholder="np. 350.00"
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="proc-notes">Notatki dodatkowe</Label>
                      <Textarea
                        id="proc-notes"
                        value={procedureForm.notes}
                        onChange={(e) =>
                          setProcedureForm({ ...procedureForm, notes: e.target.value })
                        }
                        placeholder="Dodatkowe uwagi..."
                        rows={3}
                      />
                    </div>
                  </div>

                  <Separator />

                  <div className="flex justify-end">
                    <Button type="submit" size="lg" disabled={addProcedureMutation.isPending}>
                      {addProcedureMutation.isPending ? 'Zapisywanie...' : 'Zapisz wpis o zabiegu'}
                    </Button>
                  </div>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Saved Records (Collapsible) */}
      {totalRecords > 0 && (
        <Card>
          <CardHeader
            className="cursor-pointer"
            onClick={() => setShowRecords(!showRecords)}
          >
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Zapisane wpisy ({totalRecords})</CardTitle>
                <CardDescription>
                  Kliknij, aby wyświetlić historię wprowadzonych danych
                </CardDescription>
              </div>
              {showRecords ? (
                <ChevronUp className="w-5 h-5" />
              ) : (
                <ChevronDown className="w-5 h-5" />
              )}
            </div>
          </CardHeader>
          {showRecords && (
            <CardContent>
              <div className="space-y-3">
                {/* Medications */}
                {animal.medications.map((med) => (
                  <div key={`med-${med.id}`} className="p-4 border rounded-lg bg-gray-50">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-full bg-white">
                        <Pill className="w-4 h-4 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-1">
                          <p className="text-sm text-gray-600">
                            {new Date(med.start_date).toLocaleDateString('pl-PL')}
                          </p>
                        </div>
                        <p>Przepisano lek: {med.medication_name}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          Dawkowanie: {med.dosage}, Częstotliwość: {med.frequency}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          Wykonał: {med.prescribed_by_name}
                        </p>
                        {med.notes && (
                          <p className="text-sm text-gray-500 mt-2 italic">{med.notes}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* Vaccinations */}
                {animal.vaccinations.map((vac) => (
                  <div key={`vac-${vac.id}`} className="p-4 border rounded-lg bg-gray-50">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-full bg-white">
                        <Syringe className="w-4 h-4 text-green-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-1">
                          <p className="text-sm text-gray-600">
                            {new Date(vac.vaccination_date).toLocaleDateString('pl-PL')}
                          </p>
                        </div>
                        <p>Szczepienie: {vac.vaccine_name}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          Nr partii: {vac.batch_number || '-'}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          Wykonał: {vac.administered_by_name}
                        </p>
                        {vac.notes && (
                          <p className="text-sm text-gray-500 mt-2 italic">{vac.notes}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* Procedures */}
                {animal.medical_procedures.map((proc) => (
                  <div key={`proc-${proc.id}`} className="p-4 border rounded-lg bg-gray-50">
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-full bg-white">
                        <Scissors className="w-4 h-4 text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-1">
                          <p className="text-sm text-gray-600">
                            {new Date(proc.procedure_date).toLocaleDateString('pl-PL')}
                          </p>
                        </div>
                        <p>{proc.procedure_name}</p>
                        <p className="text-sm text-gray-600 mt-1">{proc.description}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          Wykonał: {proc.performed_by_name}
                        </p>
                        {proc.outcome && (
                          <p className="text-sm text-gray-500 mt-2 italic">
                            Wynik: {proc.outcome}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          )}
        </Card>
      )}

      {/* Show info for non-employees */}
      {!canModify && totalRecords === 0 && (
        <Card>
          <CardContent className="py-8 text-center text-gray-500">
            Brak zapisanych danych medycznych dla tego zwierzęcia.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
