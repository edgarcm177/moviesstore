from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, MovieRequest,MoviePetition
from django.contrib.auth.decorators import login_required

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def petition_page(request):
    if request.method == 'POST':
        if 'vote_petition' in request.POST:
            petition_id = request.POST.get('petition_id')
            petition = get_object_or_404(MoviePetition, id=petition_id)
            if request.user in petition.votes.all():
                petition.votes.remove(request.user)
            else:
                petition.votes.add(request.user)
            return redirect('movies.petitions')

        if 'delete_petition' in request.POST:
            petition_id = request.POST.get('petition_id')
            petition = get_object_or_404(MoviePetition, id=petition_id, user=request.user)
            petition.delete()
            return redirect('movies.petitions') 

        movie_title = request.POST.get('movie_title')
        reason = request.POST.get('reason')
        if movie_title and reason:
            MoviePetition.objects.create(
                user=request.user,
                movie_title=movie_title,
                reason=reason
            )
        return redirect('movies.petitions') 

    
    all_petitions = MoviePetition.objects.all().order_by('-created_at')

    # Check approval status for each petition
    petitions_with_status = []
    for petition in all_petitions:
        is_approved = Movie.objects.filter(name__iexact=petition.movie_title).exists()
        petitions_with_status.append({
            'petition': petition,
            'is_approved': is_approved
        })

    context = {
        'title': 'Movie Petitions',
        'petitions_with_status': petitions_with_status
    }
    return render(request, 'movies/petition.html', {'template_data': context})

        

@login_required
def request_page(request):
    if request.method == 'POST':
        if 'delete_request' in request.POST:
            request_id = request.POST.get('request_id')
            movie_request = get_object_or_404(MovieRequest, id=request_id, user=request.user)
            movie_request.delete()
            return redirect('movies.requests')

        
        movie_title = request.POST.get('movie_title')
        description = request.POST.get('description')
        if movie_title and description:  
            MovieRequest.objects.create(
                user=request.user,
                movie_title=movie_title,
                description=description
            )
        return redirect('movies.requests')

    user_requests = MovieRequest.objects.filter(user=request.user).order_by('-created_at')

    requests_with_status = []
    for req in user_requests:
        is_approved = Movie.objects.filter(name__iexact=req.movie_title).exists()
        requests_with_status.append({
            'request': req,
            'is_approved': is_approved
        })
    
    context = {
        'title': 'My Movie Requests',
        'requests_with_status': requests_with_status
    }
    return render(request, 'movies/request_page.html', {'template_data': context})