'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Search, FileText, Scale, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '@/lib/auth/auth-provider';

interface SearchResult {
  content_preview: string;
  similarity_score: number;
  document_id: string;
  document_title: string;
  document_type: string;
  jurisdiction: string;
  chunk_index: number;
  citations_in_chunk: string[];
  legal_terms_in_chunk: string[];
  word_count: number;
}

interface SearchResponse {
  success: boolean;
  query: string;
  results_count: number;
  search_results: SearchResult[];
  search_metadata: any;
}

const documentTypes = [
  { value: '', label: 'All Document Types' },
  { value: 'judgment', label: 'Court Judgment' },
  { value: 'statute', label: 'Statute or Act' },
  { value: 'contract', label: 'Legal Contract' },
  { value: 'pleading', label: 'Pleading Document' },
  { value: 'opinion', label: 'Legal Opinion' },
  { value: 'article', label: 'Legal Article' },
];

const jurisdictions = [
  { value: '', label: 'All Jurisdictions' },
  { value: 'South Africa', label: 'South Africa' },
  { value: 'International', label: 'International' },
];

export default function LegalSearchInterface() {
  const [query, setQuery] = useState('');
  const [documentType, setDocumentType] = useState('');
  const [jurisdiction, setJurisdiction] = useState('');
  const [limit, setLimit] = useState(5);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const { user } = useAuth();

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setError(null);
    setSearching(true);

    try {
      const formData = new FormData();
      formData.append('query', query);
      formData.append('limit', limit.toString());
      
      if (documentType) {
        formData.append('document_type', documentType);
      }
      
      if (jurisdiction) {
        formData.append('jurisdiction', jurisdiction);
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/documents/search`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user?.token || 'demo'}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }

      const data: SearchResponse = await response.json();
      
      if (data.success) {
        setSearchResults(data.search_results);
        setHasSearched(true);
      } else {
        throw new Error('Search request failed');
      }

    } catch (err: any) {
      console.error('Search error:', err);
      setError(err.message || 'Search failed. Please try again.');
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const formatSimilarityScore = (score: number) => {
    return (score * 100).toFixed(1) + '%';
  };

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case 'judgment':
        return <Scale className="h-4 w-4" />;
      case 'contract':
        return <FileText className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Interface */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center text-primary">
            <Search className="h-5 w-5 mr-2" />
            Legal Document Search
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="bg-destructive/10 p-3 rounded-md flex items-center text-sm">
              <AlertCircle className="h-4 w-4 mr-2 text-destructive" />
              <span className="text-destructive">{error}</span>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="searchQuery">Search Query</Label>
            <Input
              id="searchQuery"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., constitutional rights, property law, contract disputes..."
              disabled={searching}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="documentType">Document Type</Label>
              <Select value={documentType} onValueChange={setDocumentType} disabled={searching}>
                <SelectTrigger id="documentType">
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  {documentTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="jurisdiction">Jurisdiction</Label>
              <Select value={jurisdiction} onValueChange={setJurisdiction} disabled={searching}>
                <SelectTrigger id="jurisdiction">
                  <SelectValue placeholder="All Jurisdictions" />
                </SelectTrigger>
                <SelectContent>
                  {jurisdictions.map((j) => (
                    <SelectItem key={j.value} value={j.value}>
                      {j.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="limit">Max Results</Label>
              <Select value={limit.toString()} onValueChange={(value) => setLimit(parseInt(value))} disabled={searching}>
                <SelectTrigger id="limit">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="5">5 Results</SelectItem>
                  <SelectItem value="10">10 Results</SelectItem>
                  <SelectItem value="15">15 Results</SelectItem>
                  <SelectItem value="20">20 Results</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button 
            onClick={handleSearch} 
            disabled={searching || !query.trim()}
            className="w-full"
          >
            {searching ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Search Legal Documents
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Search Results */}
      {hasSearched && (
        <Card>
          <CardHeader>
            <CardTitle>
              Search Results {searchResults.length > 0 && `(${searchResults.length} found)`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {searchResults.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No documents found matching your search criteria.</p>
                <p className="text-sm mt-2">Try adjusting your search terms or filters.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {searchResults.map((result, index) => (
                  <div key={index} className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {getDocumentTypeIcon(result.document_type)}
                        <h3 className="font-medium text-foreground">
                          {result.document_title}
                        </h3>
                      </div>
                      <Badge variant="secondary">
                        {formatSimilarityScore(result.similarity_score)} match
                      </Badge>
                    </div>

                    <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-3">
                      <span className="capitalize">{result.document_type}</span>
                      <span>•</span>
                      <span>{result.jurisdiction}</span>
                      <span>•</span>
                      <span>{result.word_count} words</span>
                    </div>

                    <p className="text-sm text-foreground mb-3 leading-relaxed">
                      {result.content_preview}
                    </p>

                    {result.citations_in_chunk.length > 0 && (
                      <div className="mb-2">
                        <Label className="text-xs font-medium text-muted-foreground mb-1 block">
                          Citations in this section:
                        </Label>
                        <div className="flex flex-wrap gap-1">
                          {result.citations_in_chunk.map((citation, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {citation}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {result.legal_terms_in_chunk.length > 0 && (
                      <div>
                        <Label className="text-xs font-medium text-muted-foreground mb-1 block">
                          Legal terms:
                        </Label>
                        <div className="flex flex-wrap gap-1">
                          {result.legal_terms_in_chunk.slice(0, 5).map((term, i) => (
                            <Badge key={i} variant="secondary" className="text-xs">
                              {term}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
