import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/landingpage";
import DemographicsForm from "./pages/demographicsform";
import MedicalAssistant from "./pages/medicalassistant";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/demographics" element={<DemographicsForm />} />
      <Route path="/assistant" element={<MedicalAssistant />} />
    </Routes>
  );
}

export default App;
