import { 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile
} from 'firebase/auth';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { auth, db } from './firebaseConfig';

// Login function
export const login = async (email, password) => {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;
    
    // Get user data from Firestore
    const userDoc = await getDoc(doc(db, 'users', user.uid));
    const userData = userDoc.exists() ? userDoc.data() : null;
    
    return {
      success: true,
      user: user,
      userData: userData
    };
  } catch (error) {
    return {
      success: false,
      error: getAuthErrorMessage(error.code)
    };
  }
};

// Register function (for HR to create employee accounts)
export const registerEmployee = async (email, password, employeeData) => {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;
    
    // Update display name
    await updateProfile(user, {
      displayName: employeeData.name
    });
    
    // Create user document in Firestore
    await setDoc(doc(db, 'users', user.uid), {
      uid: user.uid,
      email: email,
      name: employeeData.name,
      role: employeeData.role || 'employee',
      department: employeeData.department,
      position: employeeData.position,
      startDate: employeeData.startDate,
      manager: employeeData.manager,
      createdAt: new Date(),
      onboardingStatus: 'pending',
      profileComplete: false
    });
    
    // Create employee-specific data
    await setDoc(doc(db, 'employees', user.uid), {
      personalInfo: {
        name: employeeData.name,
        email: email,
        phone: employeeData.phone || '',
        address: employeeData.address || ''
      },
      workInfo: {
        department: employeeData.department,
        position: employeeData.position,
        startDate: employeeData.startDate,
        manager: employeeData.manager,
        employeeId: employeeData.employeeId || generateEmployeeId()
      },
      onboarding: {
        status: 'pending',
        completedTasks: [],
        documentsSubmitted: [],
        trainingCompleted: []
      }
    });
    
    return {
      success: true,
      user: user
    };
  } catch (error) {
    return {
      success: false,
      error: getAuthErrorMessage(error.code)
    };
  }
};

// Logout function
export const logout = async () => {
  try {
    await signOut(auth);
    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: 'Logout failed'
    };
  }
};

// Auth state observer
export const onAuthChange = (callback) => {
  return onAuthStateChanged(auth, callback);
};

// Get current user
export const getCurrentUser = () => {
  return auth.currentUser;
};

// Helper function to generate employee ID
const generateEmployeeId = () => {
  const timestamp = Date.now().toString().slice(-6);
  const random = Math.random().toString(36).substring(2, 5).toUpperCase();
  return `EMP${timestamp}${random}`;
};

// Helper function for auth error messages
const getAuthErrorMessage = (errorCode) => {
  switch (errorCode) {
    case 'auth/user-not-found':
      return 'No account found with this email address.';
    case 'auth/wrong-password':
      return 'Incorrect password.';
    case 'auth/email-already-in-use':
      return 'An account with this email already exists.';
    case 'auth/weak-password':
      return 'Password should be at least 6 characters.';
    case 'auth/invalid-email':
      return 'Invalid email address.';
    case 'auth/too-many-requests':
      return 'Too many failed attempts. Please try again later.';
    default:
      return 'Authentication failed. Please try again.';
  }
};
