// features/animals/AddAnimalWizard.tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ChevronLeft, ChevronRight, Check, Upload, X } from "lucide-react";
import { AsyncParentSelect } from "./animalNameLookup"
import {Tag, tagsFromApi } from "./types"
import { IntakeSourceSelector } from "./IntakeSourceHandler";

export interface NewAnimalFormData {
  name: string;
  species: "DOG" | "CAT" | "OTHER";
  breed: string;
  birth_date?: string | null;
  sex: "MALE" | "FEMALE" |"UNKNOWN";
  coat_color?: string;
  weight?: number;
  identifying_marks?: string;
  transponder_number?: string | null;
  notes?: string;
  microchipping_date?: string | null;
  behavioral_tags?: number[];
  parents?: string[];
  intakes?: {
    intake_type: string;
    animal_condition: string;
    location: string;
    notes?: string;
    source_type?: string;
    source?: any;
  };
}

interface AddAnimalWizardProps {
  open: boolean;
  onClose: () => void;
  onSave: (animal: NewAnimalFormData) => void;
  existingIds: string[];
}

export function CreateAnimalWizard({
  open,
  onClose,
  onSave,
  existingIds,
}: AddAnimalWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<Partial<NewAnimalFormData>>({
    species: "DOG",
    breed: "",
    name: "",
    birth_date: "",
    sex: "MALE",
    coat_color: "",
    weight: undefined,
    identifying_marks: "",
    transponder_number: "",
    notes: "",
    microchipping_date: "",
    behavioral_tags: [],
    parents: [],
    intakes: null,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleNext = () => {
    if (currentStep === 1 && !validateStep1()) return;
    if (currentStep === 2 && !validateStep2()) return;
    if (currentStep === 3 && !validateStep3()) return
    setCurrentStep((prev) => Math.min(prev + 1, 3));
  };

  const handleBack = () => setCurrentStep((prev) => Math.max(prev - 1, 1));

  const handleClose = () => {
    setCurrentStep(1);
    setFormData({
      species: "DOG",
      breed: "",
      name: "",
      birth_date: "",
      sex: "MALE",
      coat_color: "",
      weight: undefined,
      identifying_marks: "",
      transponder_number: null,
      notes: "",
      microchipping_date: null,
      behavioral_tags: [],
      parents: [],
      intakes:     {
        intake_type: "STRAY",       
        animal_condition: "",  
        location: "",           
        notes: "",
        source_type: "",
        source: {},
    },
    });
    setErrors({});
    onClose();
  };

  const validateStep1 = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.species?.trim()) newErrors.species = "Species is required";
    if (!formData.breed?.trim()) newErrors.breed = "Breed is required";
    if (!formData.name?.trim()) newErrors.name = "Name is required";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.coat_color?.trim()) newErrors.coat_color = "Coat color is required";
    if (!formData.weight) newErrors.weight = "Weight is required";
    if (!formData.identifying_marks?.trim()) newErrors.identifying_marks = "Identifying marks are required";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep3 = (): boolean => {
  const newErrors: Record<string, string> = {}

  if (!formData.intakes?.intake_type?.trim()) {
    newErrors.intake_type = "Intake type is required"
  }

  if (!formData.intakes?.animal_condition?.trim()) {
    newErrors.animal_condition = "Animal condition is required"
  }

  if (!formData.intakes?.location?.trim()) {
    newErrors.location = "Location is required"
  }

  setErrors(newErrors)
  return Object.keys(newErrors).length === 0
}


  const handleSave = () => {
    if (!validateStep1() || !validateStep2() || !validateStep3()) return;

    // Prepare final JSON
    const payload: NewAnimalFormData = {
      species: formData.species!,
      breed: formData.breed!,
      name: formData.name!,
      birth_date: formData.birth_date || null,
      sex: formData.sex!,
      coat_color: formData.coat_color,
      weight: formData.weight ? Number(formData.weight) : undefined,
      identifying_marks: formData.identifying_marks,
      transponder_number: formData.transponder_number || null,
      status: "NEW_INTAKE",
      notes: formData.notes,
      microchipping_date: formData.microchipping_date || null,
      behavioral_tags: formData.behavioral_tags || [],
      parents: formData.parents || [],
      intakes: formData.intakes || null,
    };

    onSave(payload);
    handleClose();
  };



  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Add New Animal - Step {currentStep} of 3</DialogTitle>
          <DialogDescription>
            {currentStep === 1 && "Enter basic information"}
            {currentStep === 2 && "Additional info"}
            {currentStep === 3 && "Review and confirm"}
          </DialogDescription>
        </DialogHeader>

        <div className="py-4 overflow-y-auto flex-1">
          {currentStep === 1 && (
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label>Species *</Label>
                <Select
                  value={formData.species}
                  onValueChange={(v: "DOG" | "CAT" | "OTHER") => setFormData({ ...formData, species: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="DOG">Dog</SelectItem>
                    <SelectItem value="CAT">Cat</SelectItem>
                    <SelectItem value="OTHER">Other</SelectItem>
                  </SelectContent>
                </Select>
                {errors.species && <p className="text-red-500">{errors.species}</p>}
              </div>

              <div className="grid gap-2">
                <Label>Breed *</Label>
                <Input
                  value={formData.breed}
                  onChange={(e) => setFormData({ ...formData, breed: e.target.value })}
                />
                {errors.breed && <p className="text-red-500">{errors.breed}</p>}
              </div>

              <div className="grid gap-2">
                <Label>Name *</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
                 {errors.name && <p className="text-red-500">{errors.name}</p>}
              </div>

              <div className="grid gap-2">
                <Label>Birth Date</Label>
                <Input
                  type="date"
                  value={formData.birth_date}
                  onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
                />
              </div>

              <div className="grid gap-2">
                <Label>Sex</Label>
                <Select
                  value={formData.sex}
                  onValueChange={(v: "MALE" | "FEMALE" | "UNKNOWN") => setFormData({ ...formData, sex: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="MALE">Male</SelectItem>
                    <SelectItem value="FEMALE">Female</SelectItem>
                    <SelectItem value="UNKNOWN">Unknown</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label>Transponder number </Label>
                <Input
                  value={formData.transponder_number ?? ""}
                  onChange={(e) => setFormData({ ...formData, transponder_number: e.target.value })}
                />
              </div>


              <div className="grid gap-2">
                <Label>Microchipping date</Label>
                <Input
                  type="date"
                  value={formData.microchipping_date ?? ""}
                  onChange={(e) => setFormData({ ...formData, microchipping_date: e.target.value })}
                />
              </div>

            </div>




          )}

          {currentStep === 2 && (
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label>Coat Color *</Label>
                <Input
                  value={formData.coat_color}
                  onChange={(e) => setFormData({ ...formData, coat_color: e.target.value })}
                />
                {errors.coat_color && <p className="text-red-500">{errors.coat_color}</p>}
              </div>

              <div className="grid gap-2">
                <Label>Weight (kg) *</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={formData.weight}
                  onChange={(e) => setFormData({ ...formData, weight: Number(e.target.value) })}
                />
                {errors.weight && <p className="text-red-500">{errors.weight}</p>}
              </div>

              <div className="grid gap-2">
                <Label>Identifying Marks *</Label>
                <Textarea
                  value={formData.identifying_marks}
                  onChange={(e) => setFormData({ ...formData, identifying_marks: e.target.value })}
                  rows={3}
                />
                {errors.identifying_marks && <p className="text-red-500">{errors.identifying_marks}</p>}
              </div>

              <AsyncParentSelect
                label="Parents"
                value={formData.parents}   
                onChange={(animalIds) => setFormData({ ...formData, parents: animalIds })}
              />

               <MultiTagSelect
                 label="Behavioral tags"
                 options={tagsFromApi}
                 value={formData.behavioral_tags ?? []}
                 onChange={(ids) =>
                   setFormData({
                     ...formData,
                     behavioral_tags: ids,
                   })
                 }
               />


            </div>
          )}

{currentStep === 3 && (
  <div className="grid gap-4">
    <h3 className="text-lg font-bold">Intake Information</h3>

    <div className="grid gap-2">
      <Label>Intake Type *</Label>
      <Select
        value={formData.intakes?.intake_type || ""}
        onValueChange={(v) =>
          setFormData({
            ...formData,
            intakes: { ...(formData.intakes || {}), intake_type: v },
          })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="Select intake type" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="STRAY">Stray</SelectItem>
          <SelectItem value="SURRENDER">Surrender</SelectItem>
          <SelectItem value="TRANSFER">Transfer</SelectItem>
          <SelectItem value="CONFISCATION">Confiscation</SelectItem>
          <SelectItem value="BORN_IN_SHELTER">Born in shelter</SelectItem>
        </SelectContent>
      </Select>
      {errors.intake_type && ( <p className="text-red-500">{errors.intake_type}</p>
)}

    </div>

    <div className="grid gap-2">
      <Label>Animal Condition *</Label>
      <Input
        value={formData.intakes?.animal_condition || ""}
        onChange={(e) =>
          setFormData({
            ...formData,
            intakes: { ...(formData.intakes || {}), animal_condition: e.target.value },
          })
        }
      />
      {errors.animal_condition && (<p className="text-red-500">{errors.animal_condition}</p>
)}

    </div>

    <div className="grid gap-2">
      <Label>Location *</Label>
      <Input
        value={formData.intakes?.location || ""}
        onChange={(e) =>
          setFormData({
            ...formData,
            intakes: { ...(formData.intakes || {}), location: e.target.value },
          })
        }
      />
      {errors.location && (<p className="text-red-500">{errors.location}</p>
)}

    </div>

    <div className="grid gap-2">
      <Label>Notes</Label>
      <Textarea
        rows={3}
        value={formData.intakes?.notes || ""}
        onChange={(e) =>
          setFormData({
            ...formData,
            intakes: { ...(formData.intakes || {}), notes: e.target.value },
          })
        }
      />
    </div>

=<IntakeSourceSelector
  onChange={(payload) =>
    setFormData({
      ...formData,
      intakes: {
        ...(formData.intakes || {}),
        source_type: payload?.source_type,
        source: payload?.source,
      },
    })
  }
/>



  </div>
)}

        </div>

        <DialogFooter>
          <div className="flex justify-between w-full">
            <div>
              {currentStep > 1 && (
                <Button variant="outline" onClick={handleBack}>
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  Back
                </Button>
              )}
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              {currentStep < 3 ? (
                <Button onClick={handleNext}>
                  Next
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              ) : (
                <Button onClick={handleSave}>
                  <Check className="w-4 h-4 mr-1" />
                  Add Animal
                </Button>
              )}
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}


type Props = {
  label: string
  options: Tag[]
  value: number[]
  onChange: (value: number[]) => void
}


type MultiTagSelectProps = {
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


