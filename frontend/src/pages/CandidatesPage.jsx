import { useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import CandidateTable from "../components/CandidateTable";
import { paramsToFilter } from "../lib/filters";

export default function CandidatesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const extFilter = useMemo(
    () => paramsToFilter(searchParams),
    [searchParams]
  );

  return (
    <CandidateTable
      onSelect={(id) => navigate(`/candidates/${id}`)}
      extFilter={extFilter}
      onClearFilter={() => setSearchParams({})}
    />
  );
}
