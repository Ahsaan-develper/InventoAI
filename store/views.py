from django.shortcuts import render
from django.http import JsonResponse
from store.models import Item  # Sirf Item import karo

def user_home(request):
    """Main user home page — shows all products with search."""
    query = request.GET.get('q', '').strip()
    
    if query:
        products = Item.objects.filter(
            title__icontains=query
        ) | Item.objects.filter(
            description__icontains=query
        )
        products = products.distinct()
    else:
        products = Item.objects.all()

    return render(request, 'user/home.html', {
        'items': products,  # template mein 'products' loop chalega
        'search_query': query,
    })


def product_search_api(request):
    """API endpoint for live search (returns JSON)."""
    query = request.GET.get('q', '').strip()
    
    if query:
        items = Item.objects.filter(
            title__icontains=query
        ) | Item.objects.filter(
            description__icontains=query
        )
        items = items.distinct()
    else:
        items = Item.objects.all()

    # JS ke liye default values bhejo kyunki Item mein ye fields nahi hain
    data = [{
        'id': item.id,
        'title': item.title,
        'description': item.description or '',
        'price': str(item.price),
        'image_color': '#3b82f6',      # Default
        'image_icon': 'box',           # Default
        'category': 'General',         # Default
    } for item in items]

    return JsonResponse({'products': data})


def receipt_page(request):
    """Receipt / checkout summary page."""
    return render(request, 'user/receipt.html')