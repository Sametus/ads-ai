import matplotlib.pyplot as plt

phases = ['Faz 1', 'Faz 2', 'Faz 3', 'Faz 4', 'Faz 5', 'Faz 6', 'Faz 7', 'Faz 8', 'Faz 9', 'Faz 10']
rates = [77.07, 94.65, 94.34, 90.74, 75.85, 77.53, 68.48, 85.30, 73.57, 54.34]

plt.figure(figsize=(10, 6))
bars = plt.bar(phases, rates, color='#4CAF50', edgecolor='black')

plt.title('Müfredatlı Öğrenme (Curriculum Learning) Başarı Oranları', fontsize=14, fontweight='bold')
plt.xlabel('Eğitim Fazları', fontsize=12)
plt.ylabel('Başarı Oranı (%)', fontsize=12)
plt.ylim(0, 100)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add value labels on top of bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'%{yval}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Save the plot
output_path = 'c:/Users/husey/Desktop/ads_ai/docs/rapor/proje-rapor/success_rates.png'
plt.savefig(output_path, bbox_inches='tight', dpi=300)
print(f'Plot successfully saved to: {output_path}')
