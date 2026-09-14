from main1 import hello, about, view, view_patient, sort_patients

print('=== TESTING ALL ENDPOINTS ===\n')

# Test 1: hello
print('1. GET / - hello():')
print(f'   {hello()}\n')

# Test 2: about
print('2. GET /about - about():')
print(f'   {about()}\n')

# Test 3: view
print('3. GET /view - view():')
data = view()
print(f'   Patients count: {len(data)}\n')

# Test 4: patient by ID
print('4. GET /patient/P001 - view_patient(P001):')
print(f'   {view_patient("P001")}\n')

# Test 5: sort by height ascending
print('5. GET /sort?sort_by=height&order=asc - sort_patients():')
result = sort_patients('height', 'asc')
print(f'   Sorted by height (asc): {[p["name"] for p in result]}\n')

# Test 6: sort by bmi descending
print('6. GET /sort?sort_by=bmi&order=desc - sort_patients():')
result = sort_patients('bmi', 'desc')
print(f'   Sorted by bmi (desc): {[p["name"] for p in result]}\n')

print('✓ ALL TESTS PASSED!')
