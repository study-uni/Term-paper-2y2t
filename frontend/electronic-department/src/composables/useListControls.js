import { ref, computed } from "vue";

export function useListControls(itemsRef, searchFields, filterFn = null) {
  const searchQuery = ref("");
  const sortKey = ref("");
  const sortDir = ref("asc");
  const filterValue = ref("Всі");

  const filteredItems = computed(() => {
    const source = itemsRef.value;
    let list = Array.isArray(source) ? [...source] : [];

    const q = String(searchQuery.value ?? "")
      .trim()
      .toLowerCase();
    if (q) {
      list = list.filter((item) =>
        searchFields.some((field) => {
          const val = typeof field === "function" ? field(item) : item[field];
          return String(val ?? "")
            .toLowerCase()
            .includes(q);
        }),
      );
    }

    if (filterFn && filterValue.value !== "Всі") {
      list = list.filter((item) => filterFn(item, filterValue.value));
    }

    if (sortKey.value) {
      const key = sortKey.value;
      const dir = sortDir.value === "asc" ? 1 : -1;
      list.sort((a, b) => {
        const av = typeof key === "function" ? key(a) : a[key];
        const bv = typeof key === "function" ? key(b) : b[key];
        if (typeof av === "string" && typeof bv === "string") {
          return av.localeCompare(bv, "uk") * dir;
        }
        if (av < bv) return -1 * dir;
        if (av > bv) return 1 * dir;
        return 0;
      });
    }

    return list;
  });

  const toggleSort = (key) => {
    if (sortKey.value === key) {
      sortDir.value = sortDir.value === "asc" ? "desc" : "asc";
    } else {
      sortKey.value = key;
      sortDir.value = "asc";
    }
  };

  const sortIndicator = (key) => {
    if (sortKey.value !== key) return "";
    return sortDir.value === "asc" ? " ▲" : " ▼";
  };

  return {
    searchQuery,
    sortKey,
    sortDir,
    filterValue,
    filteredItems,
    toggleSort,
    sortIndicator,
  };
}
