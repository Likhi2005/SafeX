import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import SafetyCheck from './pages/SafetyCheck';
import Logs from './pages/Logs';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Sidebar />
        <Navbar />

        <main className="ml-64 pt-16 min-h-screen">
          <div className="p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/safety-check" element={<SafetyCheck />} />
              <Route path="/logs" element={<Logs />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;














// import React from 'react';
// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import Sidebar from './components/Sidebar';
// import Navbar from './components/Navbar';
// import Dashboard from './pages/Dashboard';
// import SafetyCheck from './pages/SafetyCheck';
// import Logs from './pages/Logs';
// import Settings from './pages/Settings';

// function App() {
//   return (
//     <Router>
//       <div className="min-h-screen bg-dark-bg">
//         <Sidebar />
//         <Navbar />

//         <main className="ml-64 pt-16 min-h-screen">
//           <div className="p-6">
//             <Routes>
//               <Route path="/" element={<Dashboard />} />
//               <Route path="/safety-check" element={<SafetyCheck />} />
//               <Route path="/logs" element={<Logs />} />
//               <Route path="/settings" element={<Settings />} />
//             </Routes>
//           </div>
//         </main>
//       </div>
//     </Router>
//   );
// }

// export default App;











// import React from 'react'
// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import Sidebar from './components/Sidebar';
// import Navbar from './components/Navbar';
// import Dashboard from './pages/Dashboard';
// // import SafetyCheck from './pages/SafetyCheck';
// // import Logs from './pages/Logs';

// // import { useState } from 'react'
// // import reactLogo from './assets/react.svg'
// // import viteLogo from '/vite.svg'
// // import './App.css'

// function App() {
//   return (
//     <div className='bg-background min-h-screen text-textPrimary'>
//       <Router>
//         <div className='flex'>
//           <Sidebar />

//           <div className='flex-1 flex flex-col'>
//             <Navbar />

//             <main className='flex-1 p-6'>
//               <Routes>
//                 <Route path='/' element={<Dashboard />} />
//                 <Route path='/dashboard' element={<Dashboard />} />
//                 {/* <Route path='/safety-check' element={<SafetyCheck />} /> */}
//                 {/* <Route path='/logs' element={<Logs />} /> */}
//               </Routes>
//             </main>
//           </div>
//         </div>
//       </Router>
//     </div>
//   )
// }

// export default App
