import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  Building2, 
  Search, 
  Filter,
  Star,
  Phone,
  Globe,
  MapPin,
  ChevronLeft,
  ChevronRight,
  Download,
  X,
  ExternalLink
} from 'lucide-react';
import { getBusinesses, exportBusinesses } from '../services/api';
import clsx from 'clsx';

function Businesses() {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({
    search: '',
    city: '',
    category: '',
    min_rating: '',
    has_phone: '',
    has_website: '',
    page: 1,
    per_page: 20,
    sort_by: 'rating',
    sort_order: 'desc',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['businesses', filters],
    queryFn: () => getBusinesses(filters),
  });

  const exportMutation = useMutation({
    mutationFn: (format) => exportBusinesses(format),
    onSuccess: (response, format) => {
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `isletmeler_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success(`${format.toUpperCase()} dosyası indirildi!`);
      setShowExportMenu(false);
    },
    onError: () => {
      toast.error('Dışa aktarım başarısız oldu');
    },
  });

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      city: '',
      category: '',
      min_rating: '',
      has_phone: '',
      has_website: '',
      page: 1,
      per_page: 20,
      sort_by: 'rating',
      sort_order: 'desc',
    });
  };

  const hasActiveFilters = filters.city || filters.category || filters.min_rating || 
                           filters.has_phone || filters.has_website;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-800">İşletmeler</h2>
          <p className="text-sm text-slate-500">
            {data?.total || 0} işletme bulundu
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              placeholder="İşletme ara..."
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={clsx(
              "p-2 rounded-lg border transition-colors",
              showFilters || hasActiveFilters
                ? "bg-primary-50 border-primary-300 text-primary-600"
                : "border-slate-300 text-slate-600 hover:bg-slate-50"
            )}
          >
            <Filter className="w-5 h-5" />
          </button>

          {/* Export */}
          <div className="relative">
            <button 
              onClick={() => setShowExportMenu(!showExportMenu)}
              disabled={!data?.businesses?.length}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="w-5 h-5" />
              <span className="hidden sm:inline">Excel İndir</span>
            </button>
            {showExportMenu && (
              <div className="absolute right-0 top-full mt-2 bg-white border border-slate-200 rounded-lg shadow-lg z-20 min-w-[160px]">
                <button
                  onClick={() => exportMutation.mutate('xlsx')}
                  disabled={exportMutation.isPending}
                  className="flex items-center gap-2 w-full px-4 py-3 text-left text-sm hover:bg-emerald-50 text-slate-700"
                >
                  📊 Excel (.xlsx)
                </button>
                <button
                  onClick={() => exportMutation.mutate('csv')}
                  disabled={exportMutation.isPending}
                  className="flex items-center gap-2 w-full px-4 py-3 text-left text-sm hover:bg-blue-50 text-slate-700 border-t"
                >
                  📄 CSV (.csv)
                </button>
                <button
                  onClick={() => exportMutation.mutate('json')}
                  disabled={exportMutation.isPending}
                  className="flex items-center gap-2 w-full px-4 py-3 text-left text-sm hover:bg-purple-50 text-slate-700 border-t"
                >
                  📋 JSON (.json)
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white rounded-xl border border-slate-200 p-4 animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-slate-700">Filtreler</h3>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
              >
                <X className="w-4 h-4" />
                Temizle
              </button>
            )}
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div>
              <label className="block text-xs text-slate-500 mb-1">Şehir</label>
              <input
                type="text"
                value={filters.city}
                onChange={(e) => handleFilterChange('city', e.target.value)}
                placeholder="İstanbul"
                className="w-full px-3 py-1.5 border border-slate-300 rounded text-sm"
              />
            </div>
            
            <div>
              <label className="block text-xs text-slate-500 mb-1">Kategori</label>
              <input
                type="text"
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                placeholder="Restoran"
                className="w-full px-3 py-1.5 border border-slate-300 rounded text-sm"
              />
            </div>
            
            <div>
              <label className="block text-xs text-slate-500 mb-1">Min. Puan</label>
              <select
                value={filters.min_rating}
                onChange={(e) => handleFilterChange('min_rating', e.target.value)}
                className="w-full px-3 py-1.5 border border-slate-300 rounded text-sm"
              >
                <option value="">Tümü</option>
                <option value="4">4+ ⭐</option>
                <option value="3">3+ ⭐</option>
                <option value="2">2+ ⭐</option>
              </select>
            </div>
            
            <div>
              <label className="block text-xs text-slate-500 mb-1">Telefon</label>
              <select
                value={filters.has_phone}
                onChange={(e) => handleFilterChange('has_phone', e.target.value)}
                className="w-full px-3 py-1.5 border border-slate-300 rounded text-sm"
              >
                <option value="">Tümü</option>
                <option value="true">Var</option>
                <option value="false">Yok</option>
              </select>
            </div>
            
            <div>
              <label className="block text-xs text-slate-500 mb-1">Website</label>
              <select
                value={filters.has_website}
                onChange={(e) => handleFilterChange('has_website', e.target.value)}
                className="w-full px-3 py-1.5 border border-slate-300 rounded text-sm"
              >
                <option value="">Tümü</option>
                <option value="true">Var</option>
                <option value="false">Yok</option>
              </select>
            </div>
            
            <div>
              <label className="block text-xs text-slate-500 mb-1">Sıralama</label>
              <select
                value={`${filters.sort_by}-${filters.sort_order}`}
                onChange={(e) => {
                  const [sort_by, sort_order] = e.target.value.split('-');
                  setFilters(prev => ({ ...prev, sort_by, sort_order }));
                }}
                className="w-full px-3 py-1.5 border border-slate-300 rounded text-sm"
              >
                <option value="rating-desc">Puan (Yüksek)</option>
                <option value="rating-asc">Puan (Düşük)</option>
                <option value="rating_count-desc">Yorum (Çok)</option>
                <option value="name-asc">İsim (A-Z)</option>
                <option value="created_at-desc">En Yeni</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Business List */}
      {isLoading ? (
        <div className="bg-white rounded-xl border border-slate-200">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="p-4 border-b border-slate-100 last:border-0">
              <div className="skeleton h-5 w-48 rounded mb-2"></div>
              <div className="skeleton h-4 w-72 rounded mb-2"></div>
              <div className="skeleton h-4 w-24 rounded"></div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          Veriler yüklenirken hata oluştu.
        </div>
      ) : data?.businesses?.length > 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50 text-left text-sm text-slate-600">
                  <th className="px-4 py-3 font-medium">İşletme</th>
                  <th className="px-4 py-3 font-medium hidden md:table-cell">Konum</th>
                  <th className="px-4 py-3 font-medium hidden lg:table-cell">İletişim</th>
                  <th className="px-4 py-3 font-medium text-center">Puan</th>
                  <th className="px-4 py-3 font-medium text-center">İşlemler</th>
                </tr>
              </thead>
              <tbody>
                {data.businesses.map((business) => (
                  <tr key={business.id} className="border-t border-slate-100 hover:bg-slate-50">
                    <td className="px-4 py-3">
                      <Link to={`/businesses/${business.id}`} className="block">
                        <div className="font-medium text-slate-800 hover:text-primary-600">
                          {business.name}
                        </div>
                        {business.category && (
                          <span className="text-xs text-slate-500">{business.category}</span>
                        )}
                      </Link>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <div className="flex items-center gap-1 text-sm text-slate-600">
                        <MapPin className="w-4 h-4 text-slate-400" />
                        {business.city || business.address?.substring(0, 30) || '-'}
                      </div>
                    </td>
                    <td className="px-4 py-3 hidden lg:table-cell">
                      <div className="flex items-center gap-2">
                        {business.phone && (
                          <a 
                            href={`tel:${business.phone}`}
                            className="flex items-center gap-1 text-sm text-slate-600 hover:text-primary-600"
                          >
                            <Phone className="w-4 h-4" />
                          </a>
                        )}
                        {business.website && (
                          <a 
                            href={business.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-sm text-slate-600 hover:text-primary-600"
                          >
                            <Globe className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {business.rating ? (
                        <div className="inline-flex items-center gap-1 bg-amber-50 text-amber-700 px-2 py-0.5 rounded">
                          <Star className="w-3 h-3 fill-current" />
                          <span className="text-sm font-medium">{business.rating}</span>
                          <span className="text-xs text-amber-500">({business.rating_count})</span>
                        </div>
                      ) : (
                        <span className="text-slate-400 text-sm">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex items-center justify-center gap-1">
                        <Link
                          to={`/businesses/${business.id}`}
                          className="p-1.5 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Link>
                        {business.google_maps_url && (
                          <a
                            href={business.google_maps_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded"
                          >
                            <MapPin className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100">
              <div className="text-sm text-slate-500">
                Sayfa {data.page} / {data.total_pages}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleFilterChange('page', Math.max(1, filters.page - 1))}
                  disabled={filters.page === 1}
                  className="p-2 border border-slate-300 rounded hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleFilterChange('page', Math.min(data.total_pages, filters.page + 1))}
                  disabled={filters.page === data.total_pages}
                  className="p-2 border border-slate-300 rounded hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center">
          <Building2 className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">Henüz işletme bulunmuyor.</p>
          <Link 
            to="/search"
            className="inline-block mt-4 text-primary-600 hover:text-primary-700 font-medium"
          >
            İşletme aramaya başla →
          </Link>
        </div>
      )}
    </div>
  );
}

export default Businesses;
