import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  Search as SearchIcon, 
  MapPin, 
  Building2, 
  Ruler,
  Loader2,
  Star,
  Phone,
  Globe,
  ExternalLink,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { searchBusinesses, getCategories, getSearchHistory } from '../services/api';
import clsx from 'clsx';

function Search() {
  const [formData, setFormData] = useState({
    location: '',
    business_type: '',
    radius: 5000,
    keyword: '',
  });

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  });

  const { data: history, refetch: refetchHistory } = useQuery({
    queryKey: ['search-history'],
    queryFn: () => getSearchHistory(10),
  });

  const searchMutation = useMutation({
    mutationFn: searchBusinesses,
    onSuccess: (data) => {
      toast.success(data.message);
      refetchHistory();
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Arama başarısız oldu');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.location.trim()) {
      toast.error('Lütfen bir lokasyon girin');
      return;
    }
    
    if (!formData.business_type.trim()) {
      toast.error('Lütfen bir işletme türü seçin');
      return;
    }

    searchMutation.mutate(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Search Form */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <SearchIcon className="w-5 h-5 text-primary-500" />
          İşletme Ara
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <MapPin className="w-4 h-4 inline mr-1" />
                Lokasyon
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="Kadıköy, İstanbul"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            {/* Business Type */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <Building2 className="w-4 h-4 inline mr-1" />
                İşletme Türü
              </label>
              <select
                name="business_type"
                value={formData.business_type}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">Kategori seçin...</option>
                {categories?.map((cat) => (
                  <option key={cat.name} value={cat.name_tr || cat.name}>
                    {cat.icon} {cat.name_tr || cat.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Radius */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                <Ruler className="w-4 h-4 inline mr-1" />
                Arama Yarıçapı: {(formData.radius / 1000).toFixed(1)} km
              </label>
              <input
                type="range"
                name="radius"
                value={formData.radius}
                onChange={handleChange}
                min="500"
                max="50000"
                step="500"
                className="w-full"
              />
              <div className="flex justify-between text-xs text-slate-400">
                <span>500m</span>
                <span>50km</span>
              </div>
            </div>

            {/* Keyword */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Anahtar Kelime (Opsiyonel)
              </label>
              <input
                type="text"
                name="keyword"
                value={formData.keyword}
                onChange={handleChange}
                placeholder="Ör: deniz ürünleri, organik..."
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={searchMutation.isPending}
            className={clsx(
              "w-full md:w-auto px-6 py-2 rounded-lg font-medium transition-all flex items-center justify-center gap-2",
              searchMutation.isPending
                ? "bg-slate-400 cursor-not-allowed"
                : "bg-primary-600 hover:bg-primary-700 text-white"
            )}
          >
            {searchMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Aranıyor...
              </>
            ) : (
              <>
                <SearchIcon className="w-4 h-4" />
                Ara
              </>
            )}
          </button>
        </form>
      </div>

      {/* Search Results */}
      {searchMutation.data && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
              {searchMutation.data.status === 'completed' ? (
                <CheckCircle className="w-5 h-5 text-emerald-500" />
              ) : (
                <AlertCircle className="w-5 h-5 text-amber-500" />
              )}
              Arama Sonuçları
            </h3>
            <div className="flex gap-2">
              <span className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm">
                {searchMutation.data.results_count} sonuç
              </span>
              <span className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-sm">
                {searchMutation.data.new_count} yeni
              </span>
            </div>
          </div>

          {searchMutation.data.businesses?.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {searchMutation.data.businesses.map((business) => (
                <Link
                  key={business.id}
                  to={`/businesses/${business.id}`}
                  className="border border-slate-200 rounded-lg p-4 hover:border-primary-300 hover:bg-primary-50/50 transition-all"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium text-slate-800">{business.name}</h4>
                    {business.rating && (
                      <span className="flex items-center gap-1 text-amber-500 text-sm">
                        <Star className="w-4 h-4 fill-current" />
                        {business.rating}
                      </span>
                    )}
                  </div>
                  
                  <p className="text-sm text-slate-500 mb-2">{business.address}</p>
                  
                  <div className="flex flex-wrap gap-2">
                    {business.category && (
                      <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-xs">
                        {business.category}
                      </span>
                    )}
                    {business.phone && (
                      <span className="flex items-center gap-1 text-xs text-slate-500">
                        <Phone className="w-3 h-3" />
                        Telefon var
                      </span>
                    )}
                    {business.website && (
                      <span className="flex items-center gap-1 text-xs text-slate-500">
                        <Globe className="w-3 h-3" />
                        Website var
                      </span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-center py-8">
              Bu kriterlere uygun işletme bulunamadı.
            </p>
          )}

          {searchMutation.data.results_count > 20 && (
            <div className="mt-4 text-center">
              <Link 
                to="/businesses"
                className="text-primary-600 hover:text-primary-700 font-medium inline-flex items-center gap-1"
              >
                Tüm sonuçları gör
                <ExternalLink className="w-4 h-4" />
              </Link>
            </div>
          )}
        </div>
      )}

      {/* Search History */}
      {history?.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Son Aramalar</h3>
          <div className="space-y-2">
            {history.map((item) => (
              <div 
                key={item.id}
                className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0"
              >
                <div className="flex items-center gap-3">
                  <MapPin className="w-4 h-4 text-slate-400" />
                  <span className="text-slate-700">{item.location}</span>
                  <span className="text-slate-400">•</span>
                  <span className="text-slate-500">{item.business_type}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={clsx(
                    "px-2 py-0.5 rounded text-xs",
                    item.status === 'completed' 
                      ? "bg-emerald-100 text-emerald-700"
                      : item.status === 'failed'
                      ? "bg-red-100 text-red-700"
                      : "bg-amber-100 text-amber-700"
                  )}>
                    {item.results_count} sonuç
                  </span>
                  <span className="text-xs text-slate-400">
                    {item.created_at && new Date(item.created_at).toLocaleDateString('tr-TR')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Search;
