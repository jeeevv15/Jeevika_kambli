import { useState, useEffect, useCallback } from "react";

export function useApiData(fetchFn, deps = []) {
  const [state, setState] = useState({ status: "loading", data: null, error: null });

  const load = useCallback(() => {
    setState((s) => ({ ...s, status: "loading", error: null }));
    fetchFn()
      .then((data) => setState({ status: "success", data, error: null }))
      .catch((err) => setState({ status: "error", data: null, error: err?.message || "Request failed" }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => { load(); }, [load]);

  return { ...state, reload: load };
}