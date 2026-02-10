import { useState, useEffect } from "react";
import { format, isSameDay } from "date-fns";
import { Calendar } from "@/components/ui/calendar";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
import apiClient from "@/api/client"


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
  duration: number;
};

// ---------------------- HELPERS ----------------------
const getStatusVariant = (status: TaskStatus) => {
  switch (status) {
    case "AVAILABLE": return "default";
    case "PERSON_LIMIT_REACHED": return "secondary";
    case "COMPLETED": return "outline";
    case "UNCOMPLETED": return "destructive";
  }
};


export function VolunteerSchedulesDetail() {
  useAuth();

  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [tasks, setTasks] = useState<Task[]>([]);
  const [myTaskIds, setMyTaskIds] = useState<string[]>([]);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [taskToSignUp, setTaskToSignUp] = useState<Task | null>(null);

  // ---------------------- FETCH TASKS ----------------------
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const res = await apiClient.get("/volunteers/tasks/");
        setTasks(
          res.data.results.map((task: any) => ({
            id: task.task_id,
            title: task.name,
            description: task.description,
            date: new Date(task.datetime),
            personLimit: task.maxVolunteers,
            volunteerCount: task.volunteers_count,
            duration: task.duration_in_minutes,
            status: task.status,
          }))
        );
      } catch (err) {
        console.error("Failed to load tasks", err);
      }
    };

    fetchTasks();
  }, []);

  // ---------------------- FETCH MY TASK IDS ----------------------
  useEffect(() => {
    const fetchMyTasks = async () => {
      try {
        const res = await apiClient.get("/volunteers/tasks/my/");
        setMyTaskIds(res.data.task_ids);
      } catch (err) {
        console.error("Failed to load my tasks", err);
      }
    };

    fetchMyTasks();
  }, []);

  // ---------------------- FILTER BY DATE ----------------------
  const tasksForSelectedDate = selectedDate
    ? tasks.filter(task => isSameDay(task.date, selectedDate))
    : [];

  const datesWithTasks = tasks.map(task => task.date);

  // ---------------------- SIGN UP ----------------------
  const handleSignUp = async (taskId: string) => {
    try {
      await apiClient.post(`/volunteers/tasks/${taskId}/signup/`);

      setMyTaskIds(prev => [...prev, taskId]);

      setTasks(prev =>
        prev.map(task =>
          task.id === taskId
            ? {
                ...task,
                volunteerCount: task.volunteerCount + 1,
                status:
                  task.volunteerCount + 1 >= task.personLimit
                    ? "PERSON_LIMIT_REACHED"
                    : "AVAILABLE",
              }
            : task
        )
      );

      setConfirmDialogOpen(false);
    } catch (err) {
      console.error("Signup failed", err);
    }
  };

  // ---------------------- CANCEL SIGN UP ----------------------
  const handleCancelSignUp = async (taskId: string) => {
    try {
      await apiClient.post(`volunteers/tasks/${taskId}/remove/`);

      setMyTaskIds(prev => prev.filter(id => id !== taskId));

      setTasks(prev =>
        prev.map(task =>
          task.id === taskId
            ? {
                ...task,
                volunteerCount: task.volunteerCount - 1,
                status: "AVAILABLE",
              }
            : task
        )
      );
    } catch (err) {
      console.error("Cancel signup failed", err);
    }
  };

  // ---------------------- UI ----------------------
  return (
    <div className="min-h-screen p-4 md:p-8 bg-gray-50">
        <div className="flex flex-col md:flex-row gap-6">
            <div className="md:w-1/2">
      {/* Calendar */}
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
      </div>

      {/* Tasks */}
      <div className="md:w-1/2 flex flex-col gap-4 overflow-y-auto max-h-screen">
      {tasksForSelectedDate.map(task => {
        const signedUp = myTaskIds.includes(task.id);
        const canSignUp =
          task.status === "AVAILABLE" ||
          (task.status === "PERSON_LIMIT_REACHED" && signedUp);

        return (
          <Card key={task.id}>
            <CardHeader>
              <CardTitle>{task.title}</CardTitle>
              <CardDescription>{task.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-gray-700">
                           <div className="flex items-center space-x-2">
               <CalendarIcon className="w-4 h-4 text-gray-500" />
               <span>{format(task.date, "PPpp")}</span>
             </div>
             <div className="flex items-center space-x-2">
               <Users className="w-4 h-4 text-gray-500" />
               <span>{task.volunteerCount} / {task.personLimit} volunteers</span>
             </div>
                <div className="flex items-center space-x-2">
               <Clock className="w-4 h-4 text-gray-500" />
               <span> {task.duration} minutes</span>
             </div>
             <div className="flex items-center space-x-2">
               <CheckCircle2 className="w-4 h-4 text-gray-500" />
               <Badge className="capitalize" variant={getStatusVariant(task.status)}>
                 {task.status.replace("_", " ")}
               </Badge>
             </div>

              {signedUp ? (
                <Button variant="outline" onClick={() => handleCancelSignUp(task.id)}>
                  Cancel Sign-Up
                </Button>
              ) : (
                <Button onClick={() => {setTaskToSignUp(task)
                  setConfirmDialogOpen(true);}
                } disabled={!canSignUp}>
                  Sign Up
                </Button>
              )}
            </CardContent>
          </Card>
        );
      })}

      {/* Confirm Dialog */}
      <AlertDialog open={confirmDialogOpen} onOpenChange={setConfirmDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm Sign-Up</AlertDialogTitle>
          </AlertDialogHeader>
          <AlertDialogDescription>
        {taskToSignUp && (
          <div className="space-y-1 text-sm text-gray-700">
            <p>
              <strong>Task:</strong> {taskToSignUp.title}
            </p>
            <p>
              <strong>Date & Time:</strong> {format(taskToSignUp.date, "PPpp")}
            </p>
            <p>
              <strong>Duration:</strong> {taskToSignUp.duration} minutes
            </p>
          </div>
        )}
          </AlertDialogDescription>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => taskToSignUp && handleSignUp(taskToSignUp.id)}
            >
              Confirm
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
    </div>
    </div>
  );
}
