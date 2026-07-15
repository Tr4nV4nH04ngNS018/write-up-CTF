# Writeup — TINY (Reverse Engineering)

> **V1t CTF 2026** · Category: Reverse Engineering · Custom ELF + Self-Decryption + Run-Length Encoding (RLE)
>
> **Flag:** `v1t{^}`

---

## 1. Tóm tắt (TL;DR)

Thử thách cung cấp một file thực thi Linux ELF 64-bit cực nhỏ (`tini_rev`, kích thước chỉ 904 bytes) không có section headers. 

Khi chạy, chương trình thực hiện:
1. Nhận chuỗi đầu vào từ người dùng qua `sys_read`.
2. Tính tổng giá trị ASCII của chuỗi đầu vào lưu vào `ebp`.
3. Giải mã 227 từ (words) cấu hình đồ họa dạng Run-length Encoding (RLE) được lưu tại địa chỉ `0x4001b8` bằng phép trừ với `ebp` (`decrypted = encrypted - ebp`).
4. Sử dụng cấu hình giải mã để dựng và in ra một lưới đồ họa kích thước 140x10. Nếu nhập đúng flag, lưới đồ họa sẽ hiển thị hình vẽ ASCII art của flag.

Bằng cách phân tích cấu trúc giải mã RLE và áp dụng các ràng buộc toán học (tổng độ dài mỗi dòng phải bằng 140 và không có giá trị run-length nào bị tràn/cắt), ta tìm được giá trị khóa chính xác duy nhất là `ebp = 625`. Với định dạng flag chuẩn `v1t{<nội dung>}`, ta tính được ký tự bên trong dấu ngoặc nhọn phải có tổng ASCII là 94, tương ứng với ký tự `^`.

---

## 2. Các file được cung cấp

| File | Vai trò | Kích thước |
|---|---|---|
| `tini_rev` | File thực thi chính của thử thách (Linux ELF 64-bit) | 904 bytes |

---

## 3. Phân tích ASM & Cơ chế hoạt động

Tiến hành disassemble mã nguồn từ điểm vào (Entry Point) của ELF tại địa chỉ `0x400070`, ta có các luồng xử lý chính như sau:

### 3.1. Đọc và tính tổng chuỗi đầu vào
Chương trình đọc tối đa 256 ký tự từ stdin và tính tổng ASCII của chúng (bỏ qua các ký tự xuống dòng `\n` và `\r`):

```assembly
0x40007b:	lea	r8, [rsp + 0x6200]       ; Buffer lưu input
0x400083:	xor	eax, eax                 ; sys_read
0x400085:	xor	edi, edi                 ; stdin
0x400087:	mov	rsi, r8
0x40008a:	mov	edx, 0x100
0x40008f:	syscall	
0x400091:	xor	ebp, ebp                 ; ebp dùng làm tổng tích lũy
0x400093:	test	rax, rax
0x400096:	jle	0x4000ae
0x400098:	mov	rsi, r8
0x40009b:	mov	rcx, rax                 ; Đọc bao nhiêu byte thì lặp bấy nhiêu lần
0x40009e:	lodsb	al, byte ptr [rsi]
0x40009f:	cmp	al, 0xa                  ; Bỏ qua '\n'
0x4000a1:	je	0x4000ac
0x4000a3:	cmp	al, 0xd                  ; Bỏ qua '\r'
0x4000a5:	je	0x4000ac
0x4000a7:	movzx	edx, al
0x4000aa:	add	ebp, edx                 ; ebp += ký tự
0x4000ac:	loop	0x40009e
```

### 3.2. Giải mã cấu hình RLE
Chương trình lặp 227 lần để giải mã các từ 16-bit bắt đầu tại địa chỉ `0x4001b8` bằng cách trừ đi `ebp` thu được, kết quả ghi vào vùng nhớ tạm thời trên stack:

```assembly
0x4000ae:	movabs	rsi, 0x4001b8
0x4000b8:	lea	r15, [rsp + 0x6000]      ; Vùng nhớ lưu cấu hình đã giải mã
0x4000c0:	mov	rdi, r15
0x4000c3:	mov	ecx, 0xe3                ; 227 từ cấu hình
0x4000c8:	movzx	eax, word ptr [rsi]
0x4000cb:	add	rsi, 2
0x4000cf:	sub	eax, ebp                 ; decrypted = encrypted - ebp
0x4000d1:	stosw	word ptr [rdi], ax
0x4000d3:	loop	0x4000c8
```

### 3.3. Dựng lưới đồ họa (RLE Decoder)
Chương trình dựng lưới 10 dòng (mỗi dòng dài tối đa 140 ký tự) dựa trên các số lượng khối màu (`0` hoặc `1`) lấy từ cấu hình đã giải mã:
- Đối với mỗi dòng:
  1. Số lượng khối (run blocks) được xác định bởi mảng tĩnh tại `0x40037e` là `[16, 20, 24, 21, 23, 22, 26, 18, 18, 26]`.
  2. Từ giải mã đầu tiên quyết định ký tự xuất phát là `'0'` hay `'1'`.
  3. Các từ giải mã tiếp theo đóng vai trò là độ dài của từng khối màu liên tục (run-length `ecx`). Sau mỗi khối, ký tự được đảo trạng thái (`xor al, 1`).
  4. Nếu giá trị giải mã `ecx` lớn hơn độ dài còn lại của dòng (`r10d`), nó sẽ bị giới hạn/cắt ngắn lại.

---

## 4. Phương pháp khai thác & Giải thuật toán học

Do chương trình không chứa bất kỳ logic so sánh hay kiểm tra hash nào của flag, flag chỉ được xác thực bằng mặt thị giác (khi chạy đúng thì in ra hình ảnh flag rõ nét). 

Tuy nhiên, ta có thể giải quyết bài toán bằng toán học thuần túy dựa trên các đặc điểm của thuật toán giải mã RLE:
1. **Ràng buộc độ dài không bị cắt**: Trong một lưới nén RLE chuẩn xác, các giá trị run-length giải mã ra phải nằm gọn trong giới hạn của dòng, tức là không bao giờ xảy ra việc run-length `ecx` lớn hơn dung lượng trống còn lại của dòng (`r10d`).
2. **Tổng độ dài chính xác**: Tổng tất cả các run-length của mỗi dòng phải bằng đúng `140`.

Ta lập trình mô phỏng lại luồng kiểm tra này và vét cạn tất cả các giá trị `ebp` từ `1` đến `65535` để tìm ra khóa giải mã hoàn hảo.

### Mã nguồn Solver (Python):

```python
# Solver tìm ebp khớp chính xác với cấu hình RLE của tini_rev

encrypted_words = [
    635, 626, 626, 641, 625, 626, 629, 637, 629, 637, 629, 637, 645, 637, 633, 641, 629, 641, 633, 632, 645, 625, 626, 629, 637, 629, 637, 629, 637, 645, 637, 633, 628, 626, 637, 629, 638, 626, 627, 633, 632, 649, 625, 626, 629, 633, 626, 628, 629, 633, 633, 639, 626, 630, 629, 629, 626, 640, 629, 641, 629, 629, 629, 640, 630, 632, 646, 626, 628, 637, 629, 633, 634, 644, 629, 645, 630, 636, 626, 628, 630, 628, 629, 641, 629, 626, 628, 630, 648, 626, 626, 626, 626, 632, 626, 629, 629, 636, 630, 645, 629, 637, 633, 641, 629, 637, 629, 638, 626, 627, 633, 626, 647, 626, 629, 626, 626, 635, 629, 637, 630, 644, 628, 627, 626, 635, 633, 641, 629, 636, 630, 638, 626, 627, 633, 651, 625, 629, 629, 629, 629, 631, 626, 634, 626, 626, 627, 636, 626, 633, 629, 645, 629, 640, 626, 644, 626, 633, 626, 626, 627, 633, 643, 625, 629, 629, 629, 628, 630, 626, 636, 629, 645, 629, 645, 629, 630, 626, 663, 629, 633, 643, 625, 632, 629, 635, 626, 630, 637, 641, 629, 645, 633, 661, 628, 626, 629, 630, 626, 628, 651, 625, 633, 629, 626, 626, 627, 626, 630, 626, 630, 626, 626, 635, 641, 628, 631, 626, 639, 633, 636, 626, 647, 626, 626, 633, 633]

r8_bytes = [16, 20, 24, 21, 23, 22, 26, 18, 18, 26]

# Thử tất cả giá trị ebp từ 1 đến 65535
for ebp in range(1, 65536):
    dec = [(w - ebp) & 0xffff for w in encrypted_words]
    r15_idx = 3
    valid = True
    
    for line_idx in range(10):
        edx = r8_bytes[line_idx]
        r15_idx += 2 # Bỏ qua từ xác định ký tự đầu
        
        r10d = 140
        for block in range(edx - 1):
            ecx = dec[r15_idx]
            r15_idx += 1
            
            # Cắt ngắn (capping) là không hợp lệ
            if ecx > r10d:
                valid = False
                break
            r10d -= ecx
            
        # Dòng phải được lấp đầy chính xác 140 ký tự
        if r10d != 0:
            valid = False
            
        if not valid:
            break
            
    if valid:
        print(f"[+] Tìm thấy ebp hợp lệ duy nhất: {ebp}")
        break
```

Chương trình cho kết quả duy nhất: **`ebp = 625`**.

### Tìm Flag từ khóa giải mã:
Ta biết định dạng flag là `v1t{<nội dung>}`:
- Tổng giá trị ASCII của tiền tố `v1t{` là `118 + 49 + 116 + 123 = 406`.
- Tổng giá trị ASCII của hậu tố `}` là `125`.
- Tổng giá trị phần nội dung bên trong dấu ngoặc nhọn:
  $$\text{sum}(\text{content}) = 625 - 406 - 125 = 94$$

Vì tổng chỉ bằng `94`, nội dung bên trong chỉ có thể là 1 ký tự (do 2 ký tự trở lên sẽ có tổng tối thiểu $32 \times 2 = 64$ hoặc $48 \times 2 = 96$ đối với các ký tự in được thông thường).
Ký tự có mã ASCII bằng 94 chính là **`^`**.

---

## 5. Flag

```
v1t{^}
```
