import { useState } from "react";
import { cn } from "@/lib/utils";
import { ChevronDown, ChevronUp, Filter, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Column {
  id: string;
  header: string;
  accessorKey: string;
  enableSorting?: boolean;
  cell?: (value: any) => React.ReactNode;
}

interface LegalDataTableProps {
  columns: Column[];
  data: any[];
  onRowClick?: (row: any) => void;
}

export function LegalDataTable({
  columns,
  data,
  onRowClick,
}: LegalDataTableProps) {
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [searchTerm, setSearchTerm] = useState("");

  const toggleSort = (columnId: string) => {
    if (sortColumn === columnId) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(columnId);
      setSortDirection("asc");
    }
  };

  const sortedData = [...data].sort((a, b) => {
    if (!sortColumn) return 0;
    
    const column = columns.find(c => c.id === sortColumn);
    if (!column) return 0;
    
    const aValue = a[column.accessorKey];
    const bValue = b[column.accessorKey];
    
    if (aValue < bValue) return sortDirection === "asc" ? -1 : 1;
    if (aValue > bValue) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  const filteredData = sortedData.filter(row => {
    if (!searchTerm) return true;
    
    return columns.some(column => {
      const value = row[column.accessorKey];
      return value && String(value).toLowerCase().includes(searchTerm.toLowerCase());
    });
  });

  return (
    <div className="w-full">
      {/* Table Controls */}
      <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <Input
          placeholder="Search..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Responsive Table */}
      <div className="overflow-x-auto rounded-md border">
        <table className="w-full min-w-[640px] table-auto">
          <thead>
            <tr className="bg-muted/50">
              {columns.map(column => (
                <th
                  key={column.id}
                  className={cn(
                    "px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider",
                    column.enableSorting && "cursor-pointer select-none"
                  )}
                  onClick={() => column.enableSorting && toggleSort(column.id)}
                >
                  <div className="flex items-center space-x-1">
                    <span>{column.header}</span>
                    {column.enableSorting && sortColumn === column.id ? (
                      sortDirection === "asc" ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )
                    ) : null}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredData.length > 0 ? (
              filteredData.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  className={cn(
                    "bg-card hover:bg-muted/50 transition-colors",
                    onRowClick && "cursor-pointer"
                  )}
                  onClick={() => onRowClick && onRowClick(row)}
                >
                  {columns.map(column => (
                    <td
                      key={`${rowIndex}-${column.id}`}
                      className="px-4 py-3 text-sm"
                    >
                      {column.cell
                        ? column.cell(row[column.accessorKey])
                        : row[column.accessorKey]}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-4 py-8 text-center text-sm text-muted-foreground"
                >
                  No results found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile Card View (only visible on very small screens) */}
      <div className="sm:hidden mt-4 space-y-2">
        {filteredData.length > 0 ? (
          filteredData.map((row, rowIndex) => (
            <div
              key={rowIndex}
              className={cn(
                "bg-card rounded-md border p-4 hover:bg-muted/50 transition-colors",
                onRowClick && "cursor-pointer"
              )}
              onClick={() => onRowClick && onRowClick(row)}
            >
              {columns.map(column => (
                <div key={`${rowIndex}-${column.id}`} className="mb-2">
                  <div className="text-xs font-medium text-muted-foreground">
                    {column.header}
                  </div>
                  <div className="text-sm">
                    {column.cell
                      ? column.cell(row[column.accessorKey])
                      : row[column.accessorKey]}
                  </div>
                </div>
              ))}
            </div>
          ))
        ) : (
          <div className="p-8 text-center text-sm text-muted-foreground">
            No results found
          </div>
        )}
      </div>
    </div>
  );
}
