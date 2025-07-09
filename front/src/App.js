import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/landingpage";
import DemographicsForm from "./pages/demographicsform";
import MedicalAssistant from "./pages/medicalassistant";
import { Toaster } from "react-hot-toast";
import ConditionInfoPage from "./pages/conditionInfoPage";

function App() {
  return (
    <>
      <Toaster position="top-center" reverseOrder={false} />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/demographics" element={<DemographicsForm />} />
        <Route path="/assistant" element={<MedicalAssistant />} />
        <Route path="/condition-info" element={<ConditionInfoPage />} />
      </Routes>
    </>
  );
}

export default App;
