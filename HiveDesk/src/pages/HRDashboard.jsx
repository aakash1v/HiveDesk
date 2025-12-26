import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  FaPlus,
  FaSearch,
  FaFilter,
  FaUserPlus,
  FaFileUpload,
  FaChartBar,
  FaBell,
  FaEdit,
  FaTrash,
  FaBuilding,
} from 'react-icons/fa'

import { auth } from '../services/firebaseConfig'
import {
  collection,
  addDoc,
  getDocs,
  deleteDoc,
  doc,
  serverTimestamp,
} from 'firebase/firestore'
import { db } from '../services/firebaseConfig'

const HRDashboard = () => {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)

  const [newEmployee, setNewEmployee] = useState({
    name: '',
    email: '',
    department: '',
    position: '',
    startDate: '',
  })

  // 🔹 Fetch employees from Firestore
  const fetchEmployees = async () => {
    try {
      const snapshot = await getDocs(collection(db, 'employees'))
      const list = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }))
      setEmployees(list)
    } catch (err) {
      toast.error('Failed to fetch employees')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEmployees()
  }, [])

  // 🔹 Stats
  const stats = {
    total: employees.length,
    onboarding: employees.filter((e) => e.status === 'Onboarding').length,
    active: employees.filter((e) => e.status === 'Active').length,
    pending: employees.filter((e) => e.status === 'Pending').length,
  }

  // 🔹 Add employee
  const handleAddEmployee = async () => {
    if (!newEmployee.name || !newEmployee.email) {
      toast.error('Please fill required fields')
      return
    }

    try {
      await addDoc(collection(db, 'employees'), {
        ...newEmployee,
        status: 'Pending',
        progress: 10,
        createdAt: serverTimestamp(),
      })

      toast.success('Employee added successfully!')
      setShowAddModal(false)
      setNewEmployee({
        name: '',
        email: '',
        department: '',
        position: '',
        startDate: '',
      })
      fetchEmployees()
    } catch (err) {
      toast.error('Failed to add employee')
    }
  }

  // 🔹 Delete employee
  const handleDeleteEmployee = async (id) => {
    try {
      await deleteDoc(doc(db, 'employees', id))
      toast.success('Employee deleted')
      fetchEmployees()
    } catch (err) {
      toast.error('Failed to delete employee')
    }
  }

  // 🔹 Logout
  const handleLogout = async () => {
    await auth.signOut()
    localStorage.clear()
    navigate('/login')
    toast.success('Logged out successfully')
  }

  const filteredEmployees = employees.filter(
    (employee) =>
      employee.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.department?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return 'bg-green-100 text-green-800'
      case 'Onboarding':
        return 'bg-blue-100 text-blue-800'
      case 'Pending':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-600">
        Loading employees...
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <FaBuilding className="text-blue-600 text-xl" />
            <span className="font-bold text-xl">HR Portal</span>
          </div>

          <button onClick={handleLogout} className="text-sm text-gray-700">
            Logout
          </button>
        </div>
      </nav>

      <div className="p-6">
        <h1 className="text-3xl font-bold mb-2">HR Dashboard</h1>
        <p className="text-gray-600 mb-6">
          Manage employee onboarding and HR operations
        </p>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard label="Total Employees" value={stats.total} icon={<FaChartBar />} />
          <StatCard label="Onboarding" value={stats.onboarding} icon={<FaUserPlus />} />
          <StatCard label="Active" value={stats.active} icon={<FaChartBar />} />
          <StatCard label="Pending" value={stats.pending} icon={<FaBell />} />
        </div>

        {/* Search + Add */}
        <div className="flex justify-between mb-6">
          <input
            placeholder="Search employees..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="border px-4 py-2 rounded-lg w-full max-w-sm"
          />
          <button
            onClick={() => setShowAddModal(true)}
            className="ml-4 bg-blue-600 text-white px-4 py-2 rounded-lg"
          >
            <FaPlus className="inline mr-1" /> Add Employee
          </button>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="min-w-full divide-y">
            <thead className="bg-gray-50">
              <tr>
                <th className="p-3 text-left">Name</th>
                <th className="p-3 text-left">Department</th>
                <th className="p-3 text-left">Status</th>
                <th className="p-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredEmployees.map((emp) => (
                <tr key={emp.id} className="border-t">
                  <td className="p-3">{emp.name}</td>
                  <td className="p-3">{emp.department}</td>
                  <td className="p-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs ${getStatusColor(
                        emp.status
                      )}`}
                    >
                      {emp.status}
                    </span>
                  </td>
                  <td className="p-3">
                    <button
                      onClick={() => handleDeleteEmployee(emp.id)}
                      className="text-red-600"
                    >
                      <FaTrash />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="font-semibold mb-4">Add New Employee</h3>

            {['name', 'email', 'department', 'position', 'startDate'].map(
              (field) => (
                <input
                  key={field}
                  placeholder={field}
                  value={newEmployee[field]}
                  onChange={(e) =>
                    setNewEmployee({ ...newEmployee, [field]: e.target.value })
                  }
                  className="border px-3 py-2 rounded w-full mb-3"
                />
              )
            )}

            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAddModal(false)}>Cancel</button>
              <button
                onClick={handleAddEmployee}
                className="bg-blue-600 text-white px-4 py-2 rounded"
              >
                Add
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// 🔹 Reusable Stat Card
const StatCard = ({ label, value, icon }) => (
  <div className="bg-white p-4 rounded-lg shadow flex items-center gap-3">
    <div className="text-blue-600">{icon}</div>
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-xl font-semibold">{value}</p>
    </div>
  </div>
)

export default HRDashboard
