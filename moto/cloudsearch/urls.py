from .responses import CloudSearchResponse

url_bases = [
    "https?://cloudsearch.(.+).amazonaws.com",
    "https?://(.+).cloudsearch.amazonaws.com",
]

url_paths = {
    '{0}/$': CloudSearchResponse().dispatch,
    '{0}/2011-02-01/documents/batch$': CloudSearchResponse().documents_batch_response,
    '{0}/2011-02-01/search$': CloudSearchResponse().search_response,
}
