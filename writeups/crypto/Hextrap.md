# Hextrap - Crypto Writeup

## Thông tin

- **Tên bài:** Hextrap
- **Thể loại:** Cryptography
- **Flag:** `v1t{six_twists_one_smooth_order}`

## Phân tích bài toán

Bài cung cấp cho chúng ta mã nguồn `chall.py` và kết quả mã hóa `output.txt` chứa public key $n$, $e$ và bản mã $c$.

### Thuật toán tạo khóa

1. Khóa $q$ là một số nguyên tố 640-bit ngẫu nhiên.
2. Khóa $p$ được sinh ra thông qua hàm `special_prime(BITS, SMOOTH_BOUND)`:
   - Một "bag" chứa các số nguyên tố Eisenstein nhỏ (norm $\le 2^{15}$) được chuẩn bị trước.
   - Hàm `smooth_hex(bits, bag)` nhân ngẫu nhiên các phần tử trong bag cùng với các unit trong vành số nguyên Eisenstein $\mathbb{Z}[\omega]$ để tạo ra $z = (x, y) \in \mathbb{Z}[\omega]$.
   - Norm của $z$ là $m = N(z) = x^2 - xy + y^2$ là một số **smooth** (chỉ chứa các thừa số nguyên tố $\le 2^{15}$).
   - Số nguyên tố $p$ được tính bằng $p = N(z-1) = (x-1)^2 - (x-1)y + y^2$.
   - Nếu $p$ là số nguyên tố 640-bit, thuật toán dừng lại và trả về $p$.

---

## Ý tưởng khai thác

Vì $p = N(z-1)$ và $m = N(z)$ là một số smooth, ta có mối liên hệ đặc biệt trong vành số nguyên Eisenstein $\mathbb{Z}[\omega]$.

Xét đường cong elliptic có phép nhân phức (Complex Multiplication - CM) bởi $\mathbb{Z}[\omega]$ dạng:
$$E: y^2 = x^3 + B$$

Đường cong này có $j$-invariant bằng $0$.
Đối với một số nguyên tố $p \equiv 1 \pmod 3$, đường cong $E \pmod p$ có 6 cấu trúc twist (sextic twists). Các cấp của đường cong và các twist của nó mod $p$ có dạng:
- $p + 1 \pm t$
- $p + 1 \pm \frac{t \pm 3s}{2}$

Trong đó $t, s$ thỏa mãn phương trình norm $4p = t^2 + 3s^2$.
Nếu ta biểu diễn số nguyên tố Eisenstein $z-1$ dưới dạng $a + b\omega$ với $a = x-1, b = y$, ta có:
$$p = N(z-1) = a^2 - ab + b^2$$
$$4p = (2a-b)^2 + 3b^2$$

Do đó ta có thể chọn $t = 2a - b$ và $s = b$.
Xét cấp của một trong các twist, ví dụ $p + 1 + t$:
$$p + 1 + t = (a^2 - ab + b^2) + 1 + (2a - b)$$

Biểu diễn thông qua $x, y$:
$$p = (x-1)^2 - (x-1)y + y^2 = x^2 - xy + y^2 - 2x + y + 1 = m - 2x + y + 1$$
$$t = 2(x-1) - y = 2x - y - 2$$

Thay vào cấp của twist:
$$p + 1 + t = (m - 2x + y + 1) + 1 + (2x - y - 2) = m$$

Như vậy, **cấp của một twist trên đường cong $y^2 = x^3 + B \pmod p$ bằng chính xác $m = N(z)$**!
Vì $m$ là một số **$2^{15}$-smooth**, đường cong elliptic này có cấp cực kỳ smooth. Ta có thể áp dụng phương pháp **Elliptic Curve Method (ECM)** trên họ đường cong $y^2 = x^3 + B$ để phân tích thừa số $n$.

---

## Thực thi khai thác

Để tối ưu hóa thời gian chạy bằng Python thuần, ta thực hiện:
1. Sử dụng tọa độ Jacobian $(X:Y:Z)$ với $a=0$ để giảm thiểu số phép nhân modular.
2. Với mỗi số nguyên tố $p_i \le 2^{15}$, lũy thừa nó lên số mũ tối đa $e_i$ sao cho $p_i^{e_i} \le 2^{15}$ (theo chuẩn ECM Phase 1). Điều này giúp giảm kích thước scalar nhân ở mỗi bước, tối ưu hóa tốc độ nhân lên gấp 40 lần.
3. Thử nghiệm trên các đường cong với tham số $B$ khác nhau (qua điểm xuất phát $x_0$). Khi gặp đúng twist có cấp chia hết cho $m$, điểm $P$ nhân với $M$ (tích các lũy thừa số nguyên tố) sẽ trở thành điểm vô cực mod $p$, dẫn tới tọa độ $Z \equiv 0 \pmod p$. Khi đó ta tìm được $p$ qua $\gcd(Z, n)$.

Chương trình đã tìm ra thừa số thành công tại đường cong $x_0 = 7$ chỉ sau chưa đầy 16 giây:
- $p = 3971164587634789113399026192514096315991628797934773099935584394633035439388594766334258365776620150043505274728443195855341627841973958963995826770119296074037237592729321872073402425949370737$
- $q = 3748220483810589669566755882957060576744772379472871070171392916477678542421486526677373954661404221027616486603318970391886391444386888979538324563143039101271482850421776119711933444343051867$

Giải mã RSA bằng khóa vừa tìm được thu được flag.

## Flag
`v1t{six_twists_one_smooth_order}`
