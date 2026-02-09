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

export interface NewAnimalFormData {
  name?: string;
  species: string;
  breed: string;
  birth_date?: string;
  sex: "MALE" | "FEMALE";
  coat_color?: string;
  weight?: number;
  identifying_marks?: string;
  transponder_number?: string | null;
  status: "NEW_INTAKE";
  notes?: string;
  microchipping_date?: string | null;
  behavioral_tags?: string[];
  parents?: string[];
  photos: {
    filename: string;
    is_identification_photo: boolean;
  }[];
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
    species: "",
    breed: "",
    name: "",
    birth_date: "",
    sex: "MALE",
    coat_color: "",
    weight: undefined,
    identifying_marks: "",
    transponder_number: null,
    status: "NEW_INTAKE",
    notes: "",
    microchipping_date: null,
    behavioral_tags: [],
    parents: [],
    photos: [],
    intakes: null,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleNext = () => {
    if (currentStep === 1 && !validateStep1()) return;
    if (currentStep === 2 && !validateStep2()) return;
    setCurrentStep((prev) => Math.min(prev + 1, 3));
  };

  const handleBack = () => setCurrentStep((prev) => Math.max(prev - 1, 1));

  const handleClose = () => {
    setCurrentStep(1);
    setFormData({
      species: "",
      breed: "",
      name: "",
      birth_date: "",
      sex: "MALE",
      coat_color: "",
      weight: undefined,
      identifying_marks: "",
      transponder_number: null,
      status: "NEW_INTAKE",
      notes: "",
      microchipping_date: null,
      behavioral_tags: [],
      parents: [],
      photos: [],
      intakes:     {
        intake_type: "",       
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
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.coat_color?.trim()) newErrors.coat_color = "Coat color is required";
    if (!formData.weight) newErrors.weight = "Weight is required";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validateStep1() || !validateStep2()) return;

    // Prepare final JSON
    const payload: NewAnimalFormData = {
      species: formData.species!,
      breed: formData.breed!,
      name: formData.name,
      birth_date: formData.birth_date,
      sex: formData.sex!,
      coat_color: formData.coat_color,
      weight: formData.weight ? Number(formData.weight) : undefined,
      identifying_marks: formData.identifying_marks,
      transponder_number: formData.transponder_number,
      status: "NEW_INTAKE",
      notes: formData.notes,
      microchipping_date: formData.microchipping_date,
      behavioral_tags: formData.behavioral_tags || [],
      parents: formData.parents || [],
      photos: [],
      intakes: formData.intakes || null,
    };

    onSave(payload);
    handleClose();
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const newPhotos: { filename: string; is_identification_photo: boolean }[] = [];
      for (let i = 0; i < files.length; i++) {
        newPhotos.push({ filename: files[i].name, is_identification_photo: i === 0 });
      }
      setFormData({ ...formData, photos: newPhotos });
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Add New Animal - Step {currentStep} of 3</DialogTitle>
          <DialogDescription>
            {currentStep === 1 && "Enter basic information"}
            {currentStep === 2 && "Appearance and health info"}
            {currentStep === 3 && "Review and confirm"}
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {currentStep === 1 && (
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label>Species *</Label>
                <Input
                  value={formData.species}
                  onChange={(e) => setFormData({ ...formData, species: e.target.value })}
                />
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
                <Label>Name</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
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
                  onValueChange={(v: "MALE" | "FEMALE") => setFormData({ ...formData, sex: v })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="MALE">Male</SelectItem>
                    <SelectItem value="FEMALE">Female</SelectItem>
                  </SelectContent>
                </Select>
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
                <Label>Identifying Marks</Label>
                <Textarea
                  value={formData.identifying_marks}
                  onChange={(e) => setFormData({ ...formData, identifying_marks: e.target.value })}
                  rows={3}
                />
              </div>

              <div className="grid gap-2">
                <Label>Photos *</Label>
                <input type="file" multiple onChange={handleFileUpload} />
                {formData.photos?.length > 0 && (
                  <div className="flex gap-2 mt-2">
                    {formData.photos.map((p, i) => (
                      <span key={i}>{p.filename}</span>
                    ))}
                  </div>
                )}
              </div>
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
        </SelectContent>
      </Select>
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

    <div className="grid gap-2">
      <Label>Source Type *</Label>
      <Select
        value={formData.intakes?.source_type || ""}
        onValueChange={(v) =>
          setFormData({
            ...formData,
            intakes: { ...(formData.intakes || {}), source_type: v },
          })
        }
      >
        <SelectTrigger>
          <SelectValue placeholder="Select source type" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="institution">Institution</SelectItem>
          <SelectItem value="person">Person</SelectItem>
        </SelectContent>
      </Select>
    </div>


        <div className="grid gap-2">
      <Label>SourceId</Label>
      <Textarea
        rows={3}
        value={formData.intakes?.source_id || ""}
        onChange={(e) =>
          setFormData({
            ...formData,
            intakes: { ...(formData.intakes || {}), source_id: e.target.value },
          })
        }
      />
    </div>


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
