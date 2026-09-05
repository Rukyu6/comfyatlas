import { initializeApp, getApps, getApp } from 'firebase/app';
import { 
  getAuth, 
  signInWithEmailAndPassword as fbSignInWithEmailAndPassword, 
  createUserWithEmailAndPassword as fbCreateUserWithEmailAndPassword, 
  signInWithPopup as fbSignInWithPopup, 
  signOut as fbSignOut, 
  onAuthStateChanged as fbOnAuthStateChanged,
  GoogleAuthProvider as fbGoogleAuthProvider,
  updateProfile as fbUpdateProfile
} from 'firebase/auth';
import { 
  getFirestore, 
  collection as fbCollection, 
  addDoc as fbAddDoc, 
  getDocs as fbGetDocs, 
  query as fbQuery, 
  where as fbWhere, 
  orderBy as fbOrderBy, 
  onSnapshot as fbOnSnapshot,
  updateDoc as fbUpdateDoc,
  doc as fbDoc,
  getDoc as fbGetDoc,
  setDoc as fbSetDoc
} from 'firebase/firestore';

const firebaseConfig = {
  apiKey: import.meta.env.PUBLIC_FIREBASE_API_KEY,
  authDomain: import.meta.env.PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.PUBLIC_FIREBASE_APP_ID
};

const isFirebaseConfigured = !!firebaseConfig.apiKey;

let app;
let auth;
let db;

if (isFirebaseConfigured && typeof window !== 'undefined') {
  // Use real Firebase
  try {
    app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();
    auth = getAuth(app);
    db = getFirestore(app);
  } catch (error) {
    console.error("Firebase initialization failed. Falling back to Mock DB.", error);
  }
}

// ==========================================
// MOCK DATABASE FALLBACK (LocalStorage-based)
// ==========================================
class MockAuth {
  constructor() {
    this.listeners = [];
    this.currentUser = null;
    
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('mock_user');
      if (stored) {
        this.currentUser = JSON.parse(stored);
      }
    }
  }

  onAuthStateChanged(callback) {
    this.listeners.push(callback);
    // Initial trigger
    setTimeout(() => callback(this.currentUser), 50);
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }

  _triggerChange() {
    this.listeners.forEach(l => l(this.currentUser));
  }
}

const mockAuthInstance = new MockAuth();

// Mock Auth functions
export const signInWithEmailAndPassword = async (authObj, email, password) => {
  if (isFirebaseConfigured && auth) {
    return fbSignInWithEmailAndPassword(auth, email, password);
  }
  
  // Mock validation
  const users = JSON.parse(localStorage.getItem('mock_users') || '[]');
  const user = users.find(u => u.email === email && u.password === password);
  if (!user) {
    throw new Error("auth/user-not-found: Invalid email or password.");
  }
  
  const userPayload = { uid: user.uid, email: user.email, displayName: email.split('@')[0] };
  mockAuthInstance.currentUser = userPayload;
  localStorage.setItem('mock_user', JSON.stringify(userPayload));
  mockAuthInstance._triggerChange();
  return { user: userPayload };
};

export const createUserWithEmailAndPassword = async (authObj, email, password) => {
  if (isFirebaseConfigured && auth) {
    return fbCreateUserWithEmailAndPassword(auth, email, password);
  }
  
  if (password.length < 6) {
    throw new Error("auth/weak-password: Password must be at least 6 characters.");
  }
  
  const users = JSON.parse(localStorage.getItem('mock_users') || '[]');
  if (users.some(u => u.email === email)) {
    throw new Error("auth/email-already-in-use: The email address is already in use.");
  }
  
  const newUid = 'uid_' + Math.random().toString(36).substr(2, 9);
  const newUser = { uid: newUid, email, password };
  users.push(newUser);
  localStorage.setItem('mock_users', JSON.stringify(users));
  
  const userPayload = { uid: newUid, email, displayName: email.split('@')[0] };
  mockAuthInstance.currentUser = userPayload;
  localStorage.setItem('mock_user', JSON.stringify(userPayload));
  mockAuthInstance._triggerChange();
  return { user: userPayload };
};

export const updateProfile = async (user, profile) => {
  if (isFirebaseConfigured && auth) {
    return fbUpdateProfile(user, profile);
  }
  // Mock profile update
  if (mockAuthInstance.currentUser) {
    mockAuthInstance.currentUser.displayName = profile.displayName;
    localStorage.setItem('mock_user', JSON.stringify(mockAuthInstance.currentUser));
    mockAuthInstance._triggerChange();
  }
  return true;
};

export const signInWithPopup = async (authObj, provider) => {
  if (isFirebaseConfigured && auth) {
    return fbSignInWithPopup(auth, provider);
  }
  
  // Simulate Google OAuth dialog delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Prompt user for simulated google signin (or default to owner/customer)
  let email = prompt("Simulate Google Sign-In: Enter your Google Email:", "rukyucrono@gmail.com");
  if (!email) email = "test_user@gmail.com";
  
  const uid = 'google_uid_' + Math.random().toString(36).substr(2, 9);
  const userPayload = { uid, email, displayName: email.split('@')[0] };
  
  mockAuthInstance.currentUser = userPayload;
  localStorage.setItem('mock_user', JSON.stringify(userPayload));
  mockAuthInstance._triggerChange();
  return { user: userPayload };
};

export const signOut = async (authObj) => {
  if (isFirebaseConfigured && auth) {
    return fbSignOut(auth);
  }
  
  mockAuthInstance.currentUser = null;
  localStorage.removeItem('mock_user');
  mockAuthInstance._triggerChange();
  return true;
};

export const onAuthStateChanged = (authObj, callback) => {
  if (isFirebaseConfigured && auth) {
    return fbOnAuthStateChanged(auth, callback);
  }
  return mockAuthInstance.onAuthStateChanged(callback);
};

export const GoogleAuthProvider = (isFirebaseConfigured && auth) ? fbGoogleAuthProvider : class MockGoogleAuthProvider {
  constructor() {
    this.providerId = 'google.com';
  }
};


// Mock Firestore functions
const getMockOrders = () => {
  if (typeof window === 'undefined') return [];
  return JSON.parse(localStorage.getItem('mock_orders') || '[]');
};

const saveMockOrders = (orders) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('mock_orders', JSON.stringify(orders));
    // Trigger custom window event to update live analytics across open tabs
    window.dispatchEvent(new CustomEvent('mock-db-update'));
  }
};

export const collection = (dbObj, name) => {
  if (isFirebaseConfigured && db) {
    return fbCollection(db, name);
  }
  return { path: name, isMock: true };
};

export const doc = (dbObj, path, id) => {
  if (isFirebaseConfigured && db) {
    return fbDoc(db, path, id);
  }
  return { path: `${path}/${id}`, id, isMock: true };
};

export const addDoc = async (collRef, data) => {
  if (isFirebaseConfigured && db) {
    return fbAddDoc(collRef, data);
  }
  
  const collPath = collRef.path;
  const prefix = collPath === 'orders' ? 'ord_' : (collPath === 'deposits' ? 'dep_' : 'doc_');
  const newId = prefix + Math.random().toString(36).substr(2, 9);
  const newDoc = { id: newId, ...data, createdAt: new Date().toISOString() };
  
  if (collPath === 'orders') {
    const orders = getMockOrders();
    orders.push(newDoc);
    saveMockOrders(orders);
  } else {
    const list = JSON.parse(localStorage.getItem(`mock_${collPath}`) || '[]');
    list.push(newDoc);
    localStorage.setItem(`mock_${collPath}`, JSON.stringify(list));
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('mock-db-update'));
    }
  }
  return { id: newId };
};

export const updateDoc = async (docRef, data) => {
  if (isFirebaseConfigured && db) {
    return fbUpdateDoc(docRef, data);
  }
  
  const path = docRef.path || '';
  const id = docRef.id;
  const parts = path.split('/');
  const collPath = parts[0];
  
  if (collPath === 'orders') {
    const orders = getMockOrders();
    const index = orders.findIndex(o => o.id === id);
    if (index !== -1) {
      orders[index] = { ...orders[index], ...data };
      saveMockOrders(orders);
    }
  } else {
    const list = JSON.parse(localStorage.getItem(`mock_${collPath}`) || '[]');
    const index = list.findIndex(item => item.id === id);
    if (index !== -1) {
      list[index] = { ...list[index], ...data };
      localStorage.setItem(`mock_${collPath}`, JSON.stringify(list));
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('mock-db-update'));
      }
    }
  }
  return true;
};

export const getDocs = async (queryObj) => {
  if (isFirebaseConfigured && db) {
    return fbGetDocs(queryObj);
  }
  
  const collPath = queryObj ? queryObj.collPath : '';
  let dataList = [];
  if (collPath === 'orders') {
    dataList = getMockOrders();
  } else {
    dataList = JSON.parse(localStorage.getItem(`mock_${collPath}`) || '[]');
  }
  
  // Resolve filters client side
  if (queryObj && queryObj.filters) {
    queryObj.filters.forEach(filter => {
      const { field, op, val } = filter;
      if (op === '==') {
        dataList = dataList.filter(o => o[field] === val);
      }
    });
  }
  
  if (queryObj && queryObj.sortField) {
    const { sortField, direction } = queryObj;
    dataList.sort((a, b) => {
      const valA = a[sortField];
      const valB = b[sortField];
      if (valA < valB) return direction === 'desc' ? 1 : -1;
      if (valA > valB) return direction === 'desc' ? -1 : 1;
      return 0;
    });
  }
  
  return {
    docs: dataList.map(doc => ({
      id: doc.id,
      data: () => doc
    }))
  };
};

export const query = (collRef, ...constraints) => {
  if (isFirebaseConfigured && db) {
    return fbQuery(collRef, ...constraints);
  }
  
  // Custom mock query construct
  const queryObj = {
    collPath: collRef.path,
    filters: [],
    sortField: null,
    direction: 'asc'
  };
  
  constraints.forEach(c => {
    if (c.type === 'where') {
      queryObj.filters.push({ field: c.field, op: c.op, val: c.val });
    } else if (c.type === 'orderBy') {
      queryObj.sortField = c.field;
      queryObj.direction = c.direction;
    }
  });
  
  return queryObj;
};

export const where = (field, op, val) => {
  return { type: 'where', field, op, val };
};

export const orderBy = (field, direction = 'asc') => {
  return { type: 'orderBy', field, direction };
};

export const onSnapshot = (queryOrRef, callback) => {
  if (isFirebaseConfigured && db) {
    return fbOnSnapshot(queryOrRef, callback);
  }
  
  // Listen for custom mock-db-update event
  const listener = async () => {
    const snapshot = await getDocs(queryOrRef);
    callback(snapshot);
  };
  
  window.addEventListener('mock-db-update', listener);
  // Initial trigger
  listener();
  
  return () => {
    window.removeEventListener('mock-db-update', listener);
  };
};

export const getDoc = async (docRef) => {
  if (isFirebaseConfigured && db) {
    return fbGetDoc(docRef);
  }
  
  const id = docRef.id;
  const path = docRef.path || '';
  const collectionName = path.split('/')[0];
  
  if (collectionName === 'users') {
    const mockUsers = JSON.parse(localStorage.getItem('mock_wallet_users') || '{}');
    const userData = mockUsers[id] || { balance_usd: 0, email: '' };
    return {
      exists: () => true,
      data: () => userData
    };
  } else if (collectionName === 'telegram_support_mappings') {
    const mockMappings = JSON.parse(localStorage.getItem('mock_support_mappings') || '{}');
    const mapping = mockMappings[id];
    return {
      exists: () => !!mapping,
      data: () => mapping
    };
  } else if (collectionName === 'orders') {
    const mockOrders = JSON.parse(localStorage.getItem('mock_orders') || '[]');
    const order = mockOrders.find(o => o.id === id);
    return {
      exists: () => !!order,
      data: () => order
    };
  }
  
  return {
    exists: () => false,
    data: () => null
  };
};

export const setDoc = async (docRef, data, options) => {
  if (isFirebaseConfigured && db) {
    return fbSetDoc(docRef, data, options);
  }
  
  const id = docRef.id;
  const path = docRef.path || '';
  const collectionName = path.split('/')[0];
  
  if (collectionName === 'users') {
    const mockUsers = JSON.parse(localStorage.getItem('mock_wallet_users') || '{}');
    mockUsers[id] = data;
    localStorage.setItem('mock_wallet_users', JSON.stringify(mockUsers));
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('mock-db-update'));
    }
  } else if (collectionName === 'telegram_support_mappings') {
    const mockMappings = JSON.parse(localStorage.getItem('mock_support_mappings') || '{}');
    mockMappings[id] = data;
    localStorage.setItem('mock_support_mappings', JSON.stringify(mockMappings));
  } else if (collectionName === 'orders') {
    const mockOrders = JSON.parse(localStorage.getItem('mock_orders') || '[]');
    const idx = mockOrders.findIndex(o => o.id === id);
    if (idx !== -1) {
      mockOrders[idx] = { ...mockOrders[idx], ...data };
    } else {
      mockOrders.push({ id, ...data });
    }
    localStorage.setItem('mock_orders', JSON.stringify(mockOrders));
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('mock-db-update'));
    }
  }
  
  return true;
};

// Export active auth/db instances
export const getAuthInstance = () => {
  if (isFirebaseConfigured && typeof window !== 'undefined' && auth) {
    return auth;
  }
  return mockAuthInstance;
};

export const getDbInstance = () => {
  if (isFirebaseConfigured && typeof window !== 'undefined' && db) {
    return db;
  }
  return {};
};

export const authInstance = typeof window !== 'undefined' && isFirebaseConfigured ? (auth || mockAuthInstance) : mockAuthInstance;
export const dbInstance = typeof window !== 'undefined' && isFirebaseConfigured ? (db || {}) : {};
