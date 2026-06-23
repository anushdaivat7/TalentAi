import { useEffect, useState } from "react";
import { getJobProfile } from "../api";
import JobProfilePanel from "../components/JobProfilePanel";

export default function JobProfilePage() {
  const [profile, setProfile] = useState(null);
  useEffect(() => {
    getJobProfile().then(setProfile).catch(() => {});
  }, []);
  return <JobProfilePanel profile={profile} />;
}
