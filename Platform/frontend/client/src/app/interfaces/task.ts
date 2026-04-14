export interface Task {
  id: number;
  course: number;
  title: string;
  description: string;
  due_date: string;
  created_by: number;
  is_completed: boolean;
}
