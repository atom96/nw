# Kolorowanie grafu

## Opis rozwiązania

W module `coloring` znajduje się funkcja `graph_coloring`,
która jako wejście przyjmuje graf (jako listę wierzcholków oraz listę krawędzi), 
a także liczbę kolorów, którymi graf miałby byc pokolorowany. Jeśli
możliwe jest pokolorowanie grafu taką liczbą kolorów, to zwracane jest poprawne
kolorowanie -mapa z wierzchołka w numer koloru. W przeciwnym przypadku 
wynikem jest `None`

## Uruchomienie

Do korzystania z rozwiązania należy zainstalować paczki
wylistowane w pliku `requirements.txt`, najprościej zrobić to komendą

```bash
pip install -r requirements.txt
```
Rozwiązanie testowane było z wykorzystaniem Pythona w wersji 3.7

## Testowanie

W folderze `tests` znajdują się testy opisanej funkcji oraz plik
`README` opisujący, jak je uruchomić.