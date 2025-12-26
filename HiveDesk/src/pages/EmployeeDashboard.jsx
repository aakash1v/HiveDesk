import React, { useEffect, useState } from 'react'
import {
  FaTasks,
  FaGraduationCap,
  FaFileAlt,
  FaUser,
  FaCalendarAlt,
  FaCheckCircle,
  FaClock,
  FaBuilding,
} from 'react-icons/fa'

import { auth, db } from '../services/firebaseConfig'
import {
  collection,
  getDocs,
  query,
  where,
  updateDoc,
  doc,
} from 'firebase/firestore'
import toast from 'react-hot-toast'

const EmployeeDashboard = () => {
  const user = auth.currentUser
  const userEmail = user?.email || ''

  const [tasks, setTasks] = useState([])
  const [trainings, setTrainings] = useState([])
  const [loading, setLoading] = useState(true)

  // 🔹 Fetch Tasks
  const fetchTasks = async () => {
    const q = query(
      collection(db, 'tasks'),
      where('employeeEmail', '==', userEmail)
    )
    const snapshot = await getDocs(q)
    setTasks(snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() })))
  }

  // 🔹 Fetch Trainings
  const fetchTrainings = async () => {
    const q = query(
      collection(db, 'trainings'),
      where('employeeEmail', '==', userEmail)
    )
    const snapshot = await getDocs(q)
    setTrainings(snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() })))
  }

  useEffect(() => {
    if (userEmail) {
      Promise.all([fetchTasks(), fetchTrainings()]).finally(() =>
        setLoading(false)
      )
    }
  }, [userEmail])

  // 🔹 Toggle task
  const toggleTask = async (id, completed) => {
    await updateDoc(doc(db, 'tasks', id), { completed: !completed })
    fetchTasks()
  }

  // 🔹 Toggle training
  const toggleTraining = async (id, completed) => {
    await updateDoc(doc(db, 'trainings', id), { completed: !completed })
    fetchTrainings()
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading dashboard...
      </div>
    )
  }

  const completedTasks = tasks.filter((t) => t.completed).length
  const taskProgress = Math.round((completedTasks / tasks.length) * 100) || 0

  const completedTrainings = trainings.filter((t) => t.completed).length
  const trainingProgress =
    Math.round((completedTrainings / trainings.length) * 100) || 0

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <FaBuilding className="text-blue-600 text-xl" />
            <span className="font-bold text-xl">Employee Portal</span>
          </div>
          <div className="text-sm text-gray-700">
            {userEmail}
          </div>
        </div>
      </nav>

      <div className="p-6">
        {/* Welcome */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-2xl p-8 mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back 👋
          </h1>
          <p>Your onboarding is progressing smoothly.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Tasks */}
          <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow">
            <div className="flex items-center mb-4">
              <FaTasks className="text-blue-600 mr-2" />
              <h2 className="text-xl font-semibold">Onboarding Tasks</h2>
            </div>

            {tasks.map((task) => (
              <div
                key={task.id}
                className={`p-4 mb-3 rounded-lg border ${
                  task.completed ? 'bg-green-50' : 'bg-gray-50'
                }`}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <p
                      className={`font-medium ${
                        task.completed && 'line-through text-gray-500'
                      }`}
                    >
                      {task.title}
                    </p>
                    <p className="text-sm text-gray-500">
                      Due: {task.dueDate}
                    </p>
                  </div>
                  <button
                    onClick={() => toggleTask(task.id, task.completed)}
                    className="text-sm px-3 py-1 rounded bg-blue-100 text-blue-700"
                  >
                    {task.completed ? 'Undo' : 'Complete'}
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Trainings */}
          <div className="bg-white p-6 rounded-xl shadow">
            <div className="flex items-center mb-4">
              <FaGraduationCap className="text-purple-600 mr-2" />
              <h2 className="text-xl font-semibold">Trainings</h2>
            </div>

            {trainings.map((training) => (
              <div
                key={training.id}
                className="p-4 mb-3 border rounded-lg"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-medium">{training.title}</p>
                    <p className="text-sm text-gray-500">
                      {training.duration}
                    </p>
                  </div>
                  <button
                    onClick={() =>
                      toggleTraining(training.id, training.completed)
                    }
                    className={`text-sm px-3 py-1 rounded ${
                      training.completed
                        ? 'bg-purple-100 text-purple-700'
                        : 'bg-purple-600 text-white'
                    }`}
                  >
                    {training.completed ? 'Completed' : 'Start'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmployeeDashboard
