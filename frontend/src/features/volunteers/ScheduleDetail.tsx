import { useState, useEffect } from "react";
import { format, isSameDay } from "date-fns";
import { Calendar } from "@/components/ui/calendar";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { CheckCircle2, Users, Calendar as CalendarIcon, Clock } from "lucide-react";
import { useAuth } from "@/features/auth/AuthContext";

// ---------------------- TYPES ----------------------
type TaskStatus = "AVAILABLE" | "PERSON_LIMIT_REACHED" | "COMPLETED" | "UNCOMPLETED";

export type Task = {
  id: string;
  title: string;
  description: string;
  date: Date;
  personLimit: number;
  volunteerCount: number;
  status: TaskStatus;
};

// ---------------------- HELPERS ----------------------
const getStatusColor = (status: TaskStatus) => {
  switch (status) {
    case "AVAILABLE": return "bg-green-500";
    case "PERSON_LIMIT_REACHED": return "bg-orange-500";
    case "COMPLETED": return "bg-blue-500";
    case "UNCOMPLETED": return "bg-red-500";
  }
};

const getStatusVariant = (status: TaskStatus) => {
  switch (status) {
    case "AVAILABLE": return "default";
    case "PERSON_LIMIT_REACHED": return "secondary";
    case "COMPLETED": return "outline";
    case "UNCOMPLETED": return "destructive";
  }
};

// ---------------------- COMPONENT ----------------------
export function VolunteerSchedulesDetail({ initialTasks = [] }: { initialTasks: Task[] }) {
  const { user } = useAuth();
  const CURRENT_VOLUNTEER_ID = user?.id || "unknown";
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [taskToSignUp, setTaskToSignUp] = useState<Task | null>(null);

  // Filter tasks by selected date
const tasksForSelectedDate = selectedDate
  ? tasks.filter(task => isSameDay(task.date, selectedDate))
  : [];



  const openConfirmDialog = (task: Task) => {
    setTaskToSignUp(task);
    setConfirmDialogOpen(true);
  };

const handleSignUp = (taskId: string) => {
  setTasks(prev =>
    prev.map(task => {
      if (task.id === taskId && task.volunteerCount < task.personLimit) {
        const newVolunteerCount = task.volunteerCount + 1;
        const newStatus = newVolunteerCount >= task.personLimit ? "PERSON_LIMIT_REACHED" : "AVAILABLE";
        return { ...task, volunteerCount: newVolunteerCount, status: newStatus };
      }
      return task;
    })
  );
};

const handleCancelSignUp = (taskId: string) => {
  setTasks(prev =>
    prev.map(task => {
      if (task.id === taskId && task.volunteerCount > 0) {
        const newVolunteerCount = task.volunteerCount - 1;
        const newStatus = newVolunteerCount < task.personLimit ? "AVAILABLE" : task.status;
        return { ...task, volunteerCount: newVolunteerCount, status: newStatus };
      }
      return task;
    })
  );
};

  const datesWithTasks = tasks.map(task => task.date);

  return (
    <div className="min-h-screen p-4 md:p-8 bg-gray-50">
      <h1 className="text-2xl font-bold mb-2">Volunteer Schedule</h1>
      <p className="text-gray-600 mb-6">Browse tasks and manage your volunteer commitments.</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Select Date</CardTitle>
            <CardDescription>Click a date to see tasks</CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={setSelectedDate}
              className="rounded-md border"
              modifiers={{ hasTasks: datesWithTasks }}
              modifiersStyles={{
                hasTasks: { fontWeight: "bold", textDecoration: "underline" },
              }}
            />
          </CardContent>
        </Card>

        {/* Task List */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>{selectedDate ? format(selectedDate, "MMMM d, yyyy") : "Select a date"}</CardTitle>
            <CardDescription>
              {tasksForSelectedDate.length} task{tasksForSelectedDate.length !== 1 && "s"} available
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[600px] pr-4">
              {tasksForSelectedDate.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <CalendarIcon className="h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-gray-500">No tasks scheduled for this date</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {tasksForSelectedDate.map(task => {
                    const signedUp = false;
                    const canSignUp = task.status === "AVAILABLE" || (task.status === "PERSON_LIMIT_REACHED" && signedUp);

                    return (
                      <Card key={task.id} className={signedUp ? "border-blue-500 border-2 bg-blue-50" : ""}>
                        <CardHeader>
                          <div className="flex items-center justify-between">
                            <div>
                              <CardTitle>{task.title}</CardTitle>
                              <CardDescription>{task.description}</CardDescription>
                            </div>
                            <Badge variant={getStatusVariant(task.status)}>{task.status.replace(/_/g, " ")}</Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="flex flex-wrap items-center gap-4 mb-4">
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <Users className="h-4 w-4" />
                              <span>{task.volunteerCount} / {task.personLimit} volunteers</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm text-gray-600">
                              <Clock className="h-4 w-4" />
                              <span>{format(task.date, "PPP")}</span>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            {signedUp ? (
                              <Button variant="outline" onClick={() => handleCancelSignUp(task.id)}>
                                Cancel Sign-Up
                              </Button>
                            ) : (
                              <Button onClick={() => openConfirmDialog(task)} disabled={!canSignUp}>
                                {task.status === "PERSON_LIMIT_REACHED" ? "Join Waitlist" : "Sign Up"}
                              </Button>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Sign-Up Confirmation Dialog */}
      <AlertDialog open={confirmDialogOpen} onOpenChange={setConfirmDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm Sign-Up</AlertDialogTitle>
            <AlertDialogDescription>Please confirm that you want to sign up for this task.</AlertDialogDescription>
          </AlertDialogHeader>
          {taskToSignUp && (
            <div className="py-4 space-y-2">
              <p className="font-semibold">{taskToSignUp.title}</p>
              <p>{taskToSignUp.description}</p>
              <p>Status: <Badge variant={getStatusVariant(taskToSignUp.status)}>{taskToSignUp.status}</Badge></p>
              <p>Volunteers: {taskToSignUp.volunteerCount} / {taskToSignUp.personLimit}</p>
              <p>Date: {format(taskToSignUp.date, "PPP")}</p>
            </div>
          )}
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => taskToSignUp && handleSignUp(taskToSignUp.id)}>
              Confirm Sign-Up
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
